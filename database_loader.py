from __future__ import annotations

import math
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
            "source": _normalize_source_series(cleaned_df),
        }
    )


def _build_product_frame(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    category_column = _first_existing_column(cleaned_df, ("category", "product_category", "sub_category"))

    return pd.DataFrame(
        {
            "product_name": _text_series(cleaned_df, "product"),
            "category": _text_series(cleaned_df, category_column),
            "price": _numeric_series(cleaned_df, "price"),
            "source": _normalize_source_series(cleaned_df),
        }
    )


def _fetch_dataframe(connection, query: str, params: tuple | None = None) -> pd.DataFrame:
    cursor = connection.cursor()
    cursor.execute(query, params or ())
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


def _is_missing_scalar(value: object) -> bool:
    """Keep missing-value checks scalar-only so pandas typing stays predictable."""
    if value is None or value is pd.NA:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    return False


def _merge_unique_sources(values: Iterable[object]) -> str:
    merged_sources: list[str] = []

    for value in values:
        if _is_missing_scalar(value):
            continue

        for part in str(value).split("|"):
            normalized_part = part.strip()
            if normalized_part and normalized_part not in merged_sources:
                merged_sources.append(normalized_part)

    return "|".join(merged_sources) if merged_sources else "unknown"


def _set_autocommit(connection: object, enabled: bool) -> None:
    """Use setattr because mysql connector stubs do not expose autocommit consistently."""
    setattr(connection, "autocommit", enabled)


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
    order_key_columns = ["source"] + customer_columns + product_columns + [
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


def _count_rows_for_source(connection, table_name: str, source: str) -> int:
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `source` = %s", (source,))
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


def _get_index_columns(connection, table_name: str, index_name: str) -> list[str]:
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND INDEX_NAME = %s
        ORDER BY SEQ_IN_INDEX
        """,
        (connection.database, table_name, index_name),
    )
    columns = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return columns


def _ensure_unique_index(connection, table_name: str, index_name: str, columns: list[str]) -> None:
    existing_columns = _get_index_columns(connection, table_name, index_name)
    if existing_columns == columns:
        return

    cursor = connection.cursor()
    try:
        if existing_columns:
            cursor.execute(f"ALTER TABLE `{table_name}` DROP INDEX `{index_name}`")
        quoted_columns = ", ".join(f"`{column_name}`" for column_name in columns)
        cursor.execute(f"ALTER TABLE `{table_name}` ADD UNIQUE KEY `{index_name}` ({quoted_columns})")
    finally:
        cursor.close()


def _count_table_rows_for_dataset(connection, dataset_name: str, table_names: Iterable[str]) -> dict[str, int]:
    return {
        table_name: _count_rows_for_source(connection, table_name, dataset_name)
        for table_name in table_names
    }


def _print_table_load_stats(
    dataset_name: str,
    table_counts_before: dict[str, int],
    inserted_counts: dict[str, int],
    duplicate_skips: dict[str, int],
) -> None:
    for table_name in ("customers", "products", "orders", "fact_sales"):
        print(f"{table_name} [{dataset_name}] -> Existing rows in DB: {table_counts_before[table_name]}")
        print(f"{table_name} [{dataset_name}] -> Rows inserted: {inserted_counts[table_name]}")
        print(f"{table_name} [{dataset_name}] -> Duplicates skipped: {duplicate_skips[table_name]}")

    print("Rows inserted:", inserted_counts)
    print("Duplicates skipped:", duplicate_skips)


def _fetch_lookup_frame(connection, query: str, dataset_name: str) -> pd.DataFrame:
    return _fetch_dataframe(connection, query, (dataset_name,))


def _execute_many_if_rows(cursor, query: str, rows: list[tuple[object, ...]]) -> None:
    if rows:
        cursor.executemany(query, rows)


def _prepare_order_components(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    customers = _build_customer_frame(cleaned_df)
    products = _build_product_frame(cleaned_df)[["product_name", "category"]]
    quantity = _numeric_series(cleaned_df, "quantity", default_value=1).round().clip(lower=1).astype(int)
    order_dates = pd.to_datetime(cleaned_df["date"], errors="coerce").dt.date

    return pd.concat(
        [
            customers,
            products,
            quantity.rename("quantity"),
            order_dates.rename("order_date"),
        ],
        axis=1,
    )


def _prepare_fact_sales_components(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    customers = _build_customer_frame(cleaned_df)
    products = _build_product_frame(cleaned_df)[["product_name", "category"]]
    quantity = _numeric_series(cleaned_df, "quantity", default_value=1).round().clip(lower=1)
    price = _numeric_series(cleaned_df, "price")
    sales = _numeric_series(cleaned_df, "sales")
    order_dates = pd.to_datetime(cleaned_df["date"], errors="coerce")

    return pd.concat(
        [
            customers,
            products,
            quantity.astype(int).rename("quantity"),
            order_dates.dt.date.rename("order_date"),
            (price * quantity).fillna(sales).round(2).rename("revenue"),
            cleaned_df.get("month", order_dates.dt.month).rename("month"),
            cleaned_df.get("year", order_dates.dt.year).rename("year"),
        ],
        axis=1,
    )


def reset_database(connection) -> None:
    """Drop child tables first so a new run starts from a clean relational state."""
    reset_queries = [
        "DROP TABLE IF EXISTS fact_sales",
        "DROP TABLE IF EXISTS orders",
        "DROP TABLE IF EXISTS products",
        "DROP TABLE IF EXISTS customers",
    ]

    cursor = connection.cursor()
    try:
        _reset_transaction_state(connection)
        for query in reset_queries:
            cursor.execute(query)
        connection.commit()
        print("Database reset completed")
    except Exception:
        connection.rollback()
        print("Transaction rolled back due to error")
        raise
    finally:
        cursor.close()


def _reset_transaction_state(connection) -> None:
    """Clear any leftover transaction before starting a fresh atomic load."""
    if connection.in_transaction:
        print("Existing transaction detected; rolling back before starting a new one")
        connection.rollback()


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
    _set_autocommit(server_connection, False)
    server_cursor = server_connection.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
    server_connection.commit()
    server_cursor.close()
    server_connection.close()

    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database,
    )
    # Keep transaction boundaries explicit so repeated runs behave predictably.
    _set_autocommit(connection, False)
    return connection


def create_tables(connection) -> None:
    """Create normalized tables with primary and foreign key constraints."""
    table_queries = [
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(120) NOT NULL,
            segment VARCHAR(50) NOT NULL DEFAULT 'unknown',
            region VARCHAR(50) NOT NULL DEFAULT 'unknown',
            city VARCHAR(50) NOT NULL DEFAULT 'unknown',
            source VARCHAR(64) NOT NULL DEFAULT 'unknown',
            UNIQUE KEY unique_customer (source, customer_name, segment, region, city)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(150) NOT NULL,
            category VARCHAR(64) NOT NULL DEFAULT 'unknown',
            price DECIMAL(12, 2) NOT NULL,
            source VARCHAR(64) NOT NULL DEFAULT 'unknown',
            UNIQUE KEY unique_product (source, product_name, category)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            order_date DATE NOT NULL,
            source VARCHAR(64) NOT NULL DEFAULT 'unknown',
            UNIQUE KEY unique_order (source, customer_id, product_id, quantity, order_date),
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
            source VARCHAR(64) NOT NULL DEFAULT 'unknown',
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
    try:
        for query in table_queries:
            cursor.execute(query)

        for table_name in ("customers", "products", "orders", "fact_sales"):
            _ensure_column(connection, table_name, "source", "VARCHAR(64) NOT NULL DEFAULT 'unknown'")

        index_specs = {
            "customers": ("unique_customer", ["source", "customer_name", "segment", "region", "city"]),
            "products": ("unique_product", ["source", "product_name", "category"]),
            "orders": ("unique_order", ["source", "customer_id", "product_id", "quantity", "order_date"]),
        }
        for table_name, (index_name, columns) in index_specs.items():
            _ensure_unique_index(connection, table_name, index_name, columns)

        connection.commit()
        print(f"Database `{connection.database}` is ready.")
        print("Tables created successfully: customers, products, orders, fact_sales")
    except Exception:
        connection.rollback()
        print("Transaction rolled back due to error")
        raise
    finally:
        cursor.close()


def prepare_customers(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique customer records for the customers dimension table."""
    customers = _build_customer_frame(cleaned_df).drop_duplicates().reset_index(drop=True)
    return customers.sort_values(by=["source", "customer_name"]).reset_index(drop=True)


def prepare_products(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique products and keep one representative price per product."""
    products = _build_product_frame(cleaned_df)
    products = (
        products.groupby(["source", "product_name", "category"], as_index=False)
        .agg(price=("price", "median"))
        .sort_values(by=["source", "product_name"])
        .reset_index(drop=True)
    )
    products["price"] = products["price"].round(2)
    return products[["product_name", "category", "price", "source"]].reset_index(drop=True)


def prepare_orders(
    cleaned_df: pd.DataFrame,
    customer_lookup: pd.DataFrame,
    product_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """Map cleaned order rows to surrogate customer and product keys."""
    orders = _prepare_order_components(cleaned_df)

    orders = orders.merge(
        customer_lookup,
        on=["source", "customer_name", "segment", "region", "city"],
        how="left",
    )
    orders = orders.merge(
        product_lookup,
        on=["source", "product_name", "category"],
        how="left",
    )

    if orders["customer_id"].isna().any():
        raise ValueError("Customer lookup failed for one or more orders.")
    if orders["product_id"].isna().any():
        raise ValueError("Product lookup failed for one or more orders.")

    prepared_orders = orders[["customer_id", "product_id", "quantity", "order_date", "source"]].copy()
    prepared_orders = prepared_orders.drop_duplicates(
        subset=["source", "customer_id", "product_id", "quantity", "order_date"]
    ).reset_index(drop=True)
    prepared_orders["customer_id"] = prepared_orders["customer_id"].astype(int)
    prepared_orders["product_id"] = prepared_orders["product_id"].astype(int)
    return prepared_orders[["customer_id", "product_id", "quantity", "order_date", "source"]].reset_index(drop=True)


def prepare_fact_sales(
    cleaned_df: pd.DataFrame,
    customer_lookup: pd.DataFrame,
    product_lookup: pd.DataFrame,
    order_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """Build the analytical fact table using order and dimension keys."""
    fact_sales = _prepare_fact_sales_components(cleaned_df)

    fact_sales = fact_sales.merge(
        customer_lookup,
        on=["source", "customer_name", "segment", "region", "city"],
        how="left",
    )
    fact_sales = fact_sales.merge(
        product_lookup,
        on=["source", "product_name", "category"],
        how="left",
    )

    order_lookup = order_lookup.copy()
    order_lookup["order_date"] = pd.to_datetime(order_lookup["order_date"], errors="coerce").dt.date
    fact_sales = fact_sales.merge(
        order_lookup,
        on=["source", "customer_id", "product_id", "quantity", "order_date"],
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
    return prepared_fact_sales[
        ["customer_id", "product_id", "order_id", "revenue", "month", "year", "source"]
    ].reset_index(drop=True)


def insert_data(connection, cleaned_df: pd.DataFrame, dataset_name: str) -> dict[str, int]:
    """Insert one dataset into normalized tables using one transaction."""
    if not isinstance(cleaned_df, pd.DataFrame):
        raise TypeError("insert_data expects a single cleaned pandas DataFrame.")

    isolated_df = cleaned_df.copy()
    isolated_df["source"] = dataset_name
    customers = prepare_customers(isolated_df)
    products = prepare_products(isolated_df)
    cursor = connection.cursor()

    inserted_counts = {
        "customers": 0,
        "products": 0,
        "orders": 0,
        "fact_sales": 0,
    }
    table_counts_before = _count_table_rows_for_dataset(connection, dataset_name, inserted_counts)
    duplicate_skips = inserted_counts.copy()

    print(f"Loading dataset into MySQL: {dataset_name}")
    print("Existing dataset rows in DB:", table_counts_before)
    print("Dataset input rows:", len(isolated_df))

    conflicting_order_rows = _count_conflicting_order_rows(isolated_df)
    if conflicting_order_rows:
        print(
            "Potentially conflicting duplicate orders detected:",
            conflicting_order_rows,
            "| duplicates are evaluated only inside the current dataset.",
        )

    try:
        # Some metadata queries or a previous failed run can leave the connection mid-transaction.
        # Reset first so start_transaction() is only called on a clean connection.
        _reset_transaction_state(connection)
        connection.start_transaction()
        print("Transaction started")

        customer_rows = list(customers.itertuples(index=False, name=None))
        _execute_many_if_rows(
            cursor,
            """
            INSERT INTO customers (customer_name, segment, region, city, source)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                segment = VALUES(segment),
                region = VALUES(region),
                city = VALUES(city)
            """,
            customer_rows,
        )

        product_rows = list(products.itertuples(index=False, name=None))
        _execute_many_if_rows(
            cursor,
            """
            INSERT INTO products (product_name, category, price, source)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                price = VALUES(price)
            """,
            product_rows,
        )

        customer_lookup = _fetch_lookup_frame(
            connection,
            """
            SELECT customer_id, customer_name, segment, region, city, source
            FROM customers
            WHERE source = %s
            """,
            dataset_name,
        )
        product_lookup = _fetch_lookup_frame(
            connection,
            """
            SELECT product_id, product_name, category, source
            FROM products
            WHERE source = %s
            """,
            dataset_name,
        )

        orders = prepare_orders(isolated_df, customer_lookup, product_lookup)
        order_rows = list(orders.itertuples(index=False, name=None))
        _execute_many_if_rows(
            cursor,
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

        order_lookup = _fetch_lookup_frame(
            connection,
            """
            SELECT order_id, customer_id, product_id, quantity, order_date, source
            FROM orders
            WHERE source = %s
            """,
            dataset_name,
        )
        fact_sales = prepare_fact_sales(isolated_df, customer_lookup, product_lookup, order_lookup)
        fact_sales_rows = list(fact_sales.itertuples(index=False, name=None))
        _execute_many_if_rows(
            cursor,
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
        table_counts_after = _count_table_rows_for_dataset(connection, dataset_name, inserted_counts)

        for table_name, batch_size in table_batches.items():
            inserted_counts[table_name] = max(table_counts_after[table_name] - table_counts_before[table_name], 0)
            duplicate_skips[table_name] = max(batch_size - inserted_counts[table_name], 0)

        connection.commit()
        print("Transaction committed successfully")
    except Exception:
        connection.rollback()
        print("Transaction rolled back due to error")
        raise
    finally:
        cursor.close()

    _print_table_load_stats(dataset_name, table_counts_before, inserted_counts, duplicate_skips)
    return inserted_counts


def load_cleaned_data_to_mysql(
    cleaned_df: pd.DataFrame,
    dataset_name: str,
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str = DEFAULT_DATABASE_NAME,
    port: int | None = None,
    reset_db: bool = False,
) -> dict[str, int]:
    """Full Week 3 workflow: optionally reset, create schema, transform, and insert."""
    connection = connect_db(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
    )

    try:
        if reset_db:
            # Full refresh mode removes stale tables before recreating the same schema.
            reset_database(connection)
        create_tables(connection)
        inserted_counts = insert_data(connection, cleaned_df, dataset_name=dataset_name)
        print(f"MySQL load completed successfully in `{database}`.")
        return inserted_counts
    except Exception:
        if connection.in_transaction:
            connection.rollback()
            print("Transaction rolled back due to error")
        raise
    finally:
        connection.close()
