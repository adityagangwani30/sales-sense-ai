from __future__ import annotations

import os
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv


load_dotenv()

DEFAULT_DATABASE_NAME = "sales_sense_db"


def _first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    for column_name in candidates:
        if column_name in df.columns:
            return column_name
    return None


def _text_series(df: pd.DataFrame, column_name: str | None, default_value: str = "unknown") -> pd.Series:
    if column_name is None or column_name not in df.columns:
        return pd.Series(default_value, index=df.index, dtype="string")

    cleaned = df[column_name].astype("string").fillna(default_value).str.strip()
    cleaned = cleaned.replace({"": default_value, "<na>": default_value})
    return cleaned


def _numeric_series(df: pd.DataFrame, column_name: str, default_value: float = 0.0) -> pd.Series:
    if column_name not in df.columns:
        return pd.Series(default_value, index=df.index, dtype="float64")
    return pd.to_numeric(df[column_name], errors="coerce").fillna(default_value)


def _build_customer_frame(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    segment_column = _first_existing_column(cleaned_df, ("segment", "customer_segment"))
    region_column = _first_existing_column(cleaned_df, ("region",))
    city_column = _first_existing_column(cleaned_df, ("city",))

    return pd.DataFrame(
        {
            "customer_name": _text_series(cleaned_df, "customer"),
            "segment": _text_series(cleaned_df, segment_column),
            "region": _text_series(cleaned_df, region_column),
            "city": _text_series(cleaned_df, city_column),
        }
    )


def _build_product_frame(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    category_column = _first_existing_column(cleaned_df, ("category", "product_category", "sub_category"))

    return pd.DataFrame(
        {
            "product_name": _text_series(cleaned_df, "product"),
            "category": _text_series(cleaned_df, category_column),
            "price": _numeric_series(cleaned_df, "price"),
        }
    )


def _fetch_dataframe(connection, query: str) -> pd.DataFrame:
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    cursor.close()
    return pd.DataFrame(rows, columns=columns)


def _normalize_source_series(
    cleaned_df: pd.DataFrame,
    default_source: str = "unknown",
) -> pd.Series:
    source_series = _text_series(cleaned_df, "source", default_source)
    source_series = source_series.fillna(default_source).astype("string").str.strip()
    return source_series.replace({"": default_source, "<na>": default_source})


def _merge_unique_sources(values: Iterable[object]) -> str:
    merged_sources: list[str] = []

    for value in values:
        if pd.isna(value):
            continue

        for part in str(value).split("|"):
            normalized_part = part.strip()
            if normalized_part and normalized_part not in merged_sources:
                merged_sources.append(normalized_part)

    return "|".join(merged_sources) if merged_sources else "unknown"


def _combine_cleaned_datasets(
    cleaned_data: pd.DataFrame | Iterable[pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, int]]:
    if isinstance(cleaned_data, pd.DataFrame):
        frames = [cleaned_data]
    else:
        frames = [frame for frame in cleaned_data if isinstance(frame, pd.DataFrame)]

    if not frames:
        raise ValueError("No cleaned datasets were provided for database loading.")

    normalized_frames: list[pd.DataFrame] = []
    total_input_rows = 0

    for dataset_index, frame in enumerate(frames, start=1):
        current = frame.copy()
        current["source"] = _normalize_source_series(current, default_source=f"dataset_{dataset_index}")
        normalized_frames.append(current)
        total_input_rows += len(current)

    combined = pd.concat(normalized_frames, ignore_index=True, sort=False)
    if combined.empty:
        return combined, {"datasets": len(frames), "input_rows": 0, "duplicates_removed": 0}

    dedupe_columns = [column_name for column_name in combined.columns if column_name != "source"]
    combined = (
        combined.groupby(dedupe_columns, dropna=False, as_index=False)["source"]
        .agg(_merge_unique_sources)
        .reset_index(drop=True)
    )

    return combined, {
        "datasets": len(frames),
        "input_rows": total_input_rows,
        "duplicates_removed": total_input_rows - len(combined),
    }


def _count_conflicting_order_rows(cleaned_df: pd.DataFrame) -> int:
    customer_columns = [
        column_name
        for column_name in ("customer", "segment", "customer_segment", "region", "city")
        if column_name in cleaned_df.columns
    ]
    product_columns = [
        column_name
        for column_name in ("product", "category", "product_category", "sub_category")
        if column_name in cleaned_df.columns
    ]
    order_key_columns = customer_columns + product_columns + [
        column_name for column_name in ("quantity", "date") if column_name in cleaned_df.columns
    ]
    revenue_column = "revenue" if "revenue" in cleaned_df.columns else "sales" if "sales" in cleaned_df.columns else None

    if not order_key_columns or revenue_column is None:
        return 0

    revenue_variants = cleaned_df.groupby(order_key_columns, dropna=False)[revenue_column].nunique(dropna=True)
    return int(revenue_variants.gt(1).sum())


def _count_rows(connection, table_name: str) -> int:
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
    row_count = int(cursor.fetchone()[0])
    cursor.close()
    return row_count


def _column_exists(connection, table_name: str, column_name: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT 1
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (connection.database, table_name, column_name),
    )
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def _ensure_column(connection, table_name: str, column_name: str, definition_sql: str) -> None:
    if _column_exists(connection, table_name, column_name):
        return

    cursor = connection.cursor()
    cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {definition_sql}")
    cursor.close()


def connect_db(
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str = DEFAULT_DATABASE_NAME,
    port: int | None = None,
):
    """Create the MySQL database if needed and return a connection to it."""
    try:
        import mysql.connector
    except ImportError as exc:
        raise ImportError(
            "mysql-connector-python is required for Week 3. Install it with "
            "`pip install mysql-connector-python`."
        ) from exc

    host = host or os.getenv("MYSQL_HOST")
    user = user or os.getenv("MYSQL_USER")
    password = password if password is not None else os.getenv("MYSQL_PASSWORD")
    database = database or os.getenv("MYSQL_DB") or DEFAULT_DATABASE_NAME
    port = port or int(os.getenv("MYSQL_PORT", "3306"))

    if not host:
        raise ValueError("MYSQL_HOST not set in .env file")
    if not user:
        raise ValueError("MYSQL_USER not set in .env file")

    print("Connecting to MySQL database...")

    server_connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
    )
    server_cursor = server_connection.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
    server_cursor.close()
    server_connection.close()

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database,
    )


def create_tables(connection) -> None:
    """Create normalized tables with primary and foreign key constraints."""
    table_queries = [
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(255) NOT NULL,
            segment VARCHAR(100) NOT NULL DEFAULT 'unknown',
            region VARCHAR(100) NOT NULL DEFAULT 'unknown',
            city VARCHAR(100) NOT NULL DEFAULT 'unknown',
            UNIQUE KEY unique_customer (customer_name, segment, region, city)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL DEFAULT 'unknown',
            price DECIMAL(12, 2) NOT NULL,
            UNIQUE KEY unique_product (product_name, category)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            order_date DATE NOT NULL,
            source VARCHAR(255) NOT NULL DEFAULT 'unknown',
            UNIQUE KEY unique_order (customer_id, product_id, quantity, order_date),
            CONSTRAINT fk_orders_customer
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            CONSTRAINT fk_orders_product
                FOREIGN KEY (product_id) REFERENCES products(product_id)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS fact_sales (
            sale_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            product_id INT NOT NULL,
            order_id INT NOT NULL,
            revenue DECIMAL(12, 2) NOT NULL,
            month TINYINT NOT NULL,
            year SMALLINT NOT NULL,
            source VARCHAR(255) NOT NULL DEFAULT 'unknown',
            UNIQUE KEY unique_sale (order_id),
            CONSTRAINT fk_fact_sales_customer
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            CONSTRAINT fk_fact_sales_product
                FOREIGN KEY (product_id) REFERENCES products(product_id),
            CONSTRAINT fk_fact_sales_order
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ) ENGINE=InnoDB
        """,
    ]

    cursor = connection.cursor()
    for query in table_queries:
        cursor.execute(query)
    cursor.close()

    _ensure_column(connection, "orders", "source", "VARCHAR(255) NOT NULL DEFAULT 'unknown'")
    _ensure_column(connection, "fact_sales", "source", "VARCHAR(255) NOT NULL DEFAULT 'unknown'")

    connection.commit()
    print(f"Database `{connection.database}` is ready.")
    print("Tables created successfully: customers, products, orders, fact_sales")


def prepare_customers(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique customer records for the customers dimension table."""
    customers = _build_customer_frame(cleaned_df).drop_duplicates().reset_index(drop=True)
    return customers.sort_values(by="customer_name").reset_index(drop=True)


def prepare_products(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique products and keep one representative price per product."""
    products = _build_product_frame(cleaned_df)
    products = (
        products.groupby(["product_name", "category"], as_index=False)
        .agg(price=("price", "median"))
        .sort_values(by="product_name")
        .reset_index(drop=True)
    )
    products["price"] = products["price"].round(2)
    return products


def prepare_orders(
    cleaned_df: pd.DataFrame,
    customer_lookup: pd.DataFrame,
    product_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """Map cleaned order rows to surrogate customer and product keys."""
    customers = _build_customer_frame(cleaned_df)
    products = _build_product_frame(cleaned_df)[["product_name", "category"]]

    orders = pd.concat(
        [
            customers,
            products,
            _numeric_series(cleaned_df, "quantity", default_value=1).round().clip(lower=1).astype(int).rename("quantity"),
            pd.to_datetime(cleaned_df["date"], errors="coerce").dt.date.rename("order_date"),
            _normalize_source_series(cleaned_df).rename("source"),
        ],
        axis=1,
    )

    orders = orders.merge(
        customer_lookup,
        on=["customer_name", "segment", "region", "city"],
        how="left",
    )
    orders = orders.merge(
        product_lookup,
        on=["product_name", "category"],
        how="left",
    )

    if orders["customer_id"].isna().any():
        raise ValueError("Customer lookup failed for one or more orders.")
    if orders["product_id"].isna().any():
        raise ValueError("Product lookup failed for one or more orders.")

    prepared_orders = orders[["customer_id", "product_id", "quantity", "order_date", "source"]].copy()
    prepared_orders = (
        prepared_orders.groupby(
            ["customer_id", "product_id", "quantity", "order_date"],
            as_index=False,
            dropna=False,
        )["source"]
        .agg(_merge_unique_sources)
        .reset_index(drop=True)
    )
    prepared_orders["customer_id"] = prepared_orders["customer_id"].astype(int)
    prepared_orders["product_id"] = prepared_orders["product_id"].astype(int)
    return prepared_orders.reset_index(drop=True)


def prepare_fact_sales(
    cleaned_df: pd.DataFrame,
    customer_lookup: pd.DataFrame,
    product_lookup: pd.DataFrame,
    order_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """Build the analytical fact table using order and dimension keys."""
    customers = _build_customer_frame(cleaned_df)
    products = _build_product_frame(cleaned_df)[["product_name", "category"]]
    quantity = _numeric_series(cleaned_df, "quantity", default_value=1).round().clip(lower=1)
    price = _numeric_series(cleaned_df, "price")
    sales = _numeric_series(cleaned_df, "sales")
    order_dates = pd.to_datetime(cleaned_df["date"], errors="coerce")

    fact_sales = pd.concat(
        [
            customers,
            products,
            quantity.astype(int).rename("quantity"),
            order_dates.dt.date.rename("order_date"),
            (price * quantity).fillna(sales).round(2).rename("revenue"),
            cleaned_df.get("month", order_dates.dt.month).rename("month"),
            cleaned_df.get("year", order_dates.dt.year).rename("year"),
            _normalize_source_series(cleaned_df).rename("source"),
        ],
        axis=1,
    )

    fact_sales = fact_sales.merge(
        customer_lookup,
        on=["customer_name", "segment", "region", "city"],
        how="left",
    )
    fact_sales = fact_sales.merge(
        product_lookup,
        on=["product_name", "category"],
        how="left",
    )

    order_lookup = order_lookup.copy()
    order_lookup["order_date"] = pd.to_datetime(order_lookup["order_date"], errors="coerce").dt.date
    fact_sales = fact_sales.merge(
        order_lookup,
        on=["customer_id", "product_id", "quantity", "order_date"],
        how="left",
    )

    if fact_sales["order_id"].isna().any():
        raise ValueError("Order lookup failed for one or more fact_sales rows.")

    fact_sales["month"] = pd.to_numeric(fact_sales["month"], errors="coerce")
    fact_sales["year"] = pd.to_numeric(fact_sales["year"], errors="coerce")
    fact_sales["revenue"] = fact_sales["revenue"].round(2)
    fact_sales = fact_sales.sort_values(by=["order_id", "revenue"], ascending=[True, False], na_position="last")

    prepared_fact_sales = (
        fact_sales.groupby("order_id", as_index=False, dropna=False)
        .agg(
            customer_id=("customer_id", "first"),
            product_id=("product_id", "first"),
            revenue=("revenue", "first"),
            month=("month", "first"),
            year=("year", "first"),
            source=("source", _merge_unique_sources),
        )
        .reset_index(drop=True)
    )
    prepared_fact_sales["customer_id"] = prepared_fact_sales["customer_id"].astype(int)
    prepared_fact_sales["product_id"] = prepared_fact_sales["product_id"].astype(int)
    prepared_fact_sales["order_id"] = prepared_fact_sales["order_id"].astype(int)
    prepared_fact_sales["month"] = pd.to_numeric(prepared_fact_sales["month"], errors="coerce").astype(int)
    prepared_fact_sales["year"] = pd.to_numeric(prepared_fact_sales["year"], errors="coerce").astype(int)
    prepared_fact_sales["revenue"] = prepared_fact_sales["revenue"].round(2)
    return prepared_fact_sales.reset_index(drop=True)


def insert_data(connection, cleaned_df: pd.DataFrame | Iterable[pd.DataFrame]) -> dict[str, int]:
    """Insert cleaned data into normalized tables using one transaction."""
    # Previous behavior summary:
    # - The loader appended into existing tables and relied on INSERT IGNORE + UNIQUE keys
    #   to skip only exact key collisions.
    # - Running the same dataset again was mostly idempotent, but the database load dropped
    #   the input `source` column and gave no visibility into how many rows were skipped.
    # - Loading multiple datasets into the same tables could silently collapse overlapping
    #   orders/fact rows because order-level uniqueness is broader than raw row identity.
    combined_df, combine_stats = _combine_cleaned_datasets(cleaned_df)
    customers = prepare_customers(combined_df)
    products = prepare_products(combined_df)
    cursor = connection.cursor()

    inserted_counts = {
        "customers": 0,
        "products": 0,
        "orders": 0,
        "fact_sales": 0,
    }
    table_counts_before = {table_name: _count_rows(connection, table_name) for table_name in inserted_counts}
    duplicate_skips = inserted_counts.copy()

    print("Existing rows in DB:", table_counts_before)
    print(
        "Combined input rows:",
        combine_stats["input_rows"],
        "| datasets:",
        combine_stats["datasets"],
        "| exact duplicates removed before load:",
        combine_stats["duplicates_removed"],
    )

    conflicting_order_rows = _count_conflicting_order_rows(combined_df)
    if conflicting_order_rows:
        print(
            "Potentially conflicting duplicate orders detected:",
            conflicting_order_rows,
            "| one fact row per order_id will be kept in MySQL.",
        )

    try:
        connection.start_transaction()

        customer_rows = list(customers.itertuples(index=False, name=None))
        if customer_rows:
            cursor.executemany(
                """
                INSERT INTO customers (customer_name, segment, region, city)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    segment = VALUES(segment),
                    region = VALUES(region),
                    city = VALUES(city)
                """,
                customer_rows,
            )

        product_rows = list(products.itertuples(index=False, name=None))
        if product_rows:
            cursor.executemany(
                """
                INSERT INTO products (product_name, category, price)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    price = VALUES(price)
                """,
                product_rows,
            )

        customer_lookup = _fetch_dataframe(
            connection,
            """
            SELECT customer_id, customer_name, segment, region, city
            FROM customers
            """,
        )
        product_lookup = _fetch_dataframe(
            connection,
            """
            SELECT product_id, product_name, category
            FROM products
            """,
        )

        orders = prepare_orders(combined_df, customer_lookup, product_lookup)
        order_rows = list(orders.itertuples(index=False, name=None))
        if order_rows:
            cursor.executemany(
                """
                INSERT INTO orders (customer_id, product_id, quantity, order_date, source)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    source = CASE
                        WHEN orders.source = VALUES(source) OR VALUES(source) = 'unknown' THEN orders.source
                        WHEN orders.source = 'unknown' THEN VALUES(source)
                        ELSE CONCAT(orders.source, '|', VALUES(source))
                    END
                """,
                order_rows,
            )

        order_lookup = _fetch_dataframe(
            connection,
            """
            SELECT order_id, customer_id, product_id, quantity, order_date
            FROM orders
            """,
        )
        fact_sales = prepare_fact_sales(combined_df, customer_lookup, product_lookup, order_lookup)
        fact_sales_rows = list(fact_sales.itertuples(index=False, name=None))
        if fact_sales_rows:
            cursor.executemany(
                """
                INSERT INTO fact_sales (customer_id, product_id, order_id, revenue, month, year, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    customer_id = VALUES(customer_id),
                    product_id = VALUES(product_id),
                    revenue = VALUES(revenue),
                    month = VALUES(month),
                    year = VALUES(year),
                    source = CASE
                        WHEN fact_sales.source = VALUES(source) OR VALUES(source) = 'unknown' THEN fact_sales.source
                        WHEN fact_sales.source = 'unknown' THEN VALUES(source)
                        ELSE CONCAT(fact_sales.source, '|', VALUES(source))
                    END
                """,
                fact_sales_rows,
            )

        table_batches = {
            "customers": len(customer_rows),
            "products": len(product_rows),
            "orders": len(order_rows),
            "fact_sales": len(fact_sales_rows),
        }
        table_counts_after = {table_name: _count_rows(connection, table_name) for table_name in inserted_counts}

        for table_name, batch_size in table_batches.items():
            inserted_counts[table_name] = max(table_counts_after[table_name] - table_counts_before[table_name], 0)
            duplicate_skips[table_name] = max(batch_size - inserted_counts[table_name], 0)

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()

    for table_name in ("customers", "products", "orders", "fact_sales"):
        print(f"{table_name} -> Existing rows in DB: {table_counts_before[table_name]}")
        print(f"{table_name} -> Rows inserted: {inserted_counts[table_name]}")
        print(f"{table_name} -> Duplicates skipped: {duplicate_skips[table_name]}")

    return inserted_counts


def load_cleaned_data_to_mysql(
    cleaned_df: pd.DataFrame | Iterable[pd.DataFrame],
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str = DEFAULT_DATABASE_NAME,
    port: int | None = None,
) -> dict[str, int]:
    """Full Week 3 workflow: connect, create schema, transform, and insert."""
    connection = connect_db(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
    )

    try:
        create_tables(connection)
        inserted_counts = insert_data(connection, cleaned_df)
        print(f"MySQL load completed successfully in `{database}`.")
        return inserted_counts
    finally:
        connection.close()
