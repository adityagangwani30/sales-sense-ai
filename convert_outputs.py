"""Convert pipeline CSV outputs into frontend-friendly JSON in `frontend/public/data/`.

This script reuses the existing `frontend_export.export_frontend_dashboard_assets`
function so the Dataset JSON, SQL analysis JSON, and visualization assets are
produced consistently with the frontend expectations.

Usage:
  python convert_outputs.py

Notes for Vercel:
 - Run this script during your build step so the generated files are included
   in the deployed `frontend/public/data/` folder (or commit the generated
   `frontend/public/data/` files into git before deploying).
"""

from __future__ import annotations

from frontend_export import export_frontend_dashboard_assets


def main() -> int:
    print("Converting CSV outputs -> frontend/public/data/...\n")
    try:
        result = export_frontend_dashboard_assets()
    except Exception as exc:
        print("Failed to export frontend dashboard assets:", exc)
        return 1

    print("Export complete. Manifest created at:")
    print(result.get("manifest"))

    # Build a simple dataset-manifest.json from any dataset JSONs present so
    # the frontend can discover available snapshots regardless of folder naming.
    from pathlib import Path
    import json

    datasets_dir = Path("frontend") / "public" / "data" / "datasets"
    manifest_path = Path("frontend") / "public" / "data" / "dataset-manifest.json"

    datasets = []
    for json_file in sorted(datasets_dir.glob("*.json")):
        dataset_id = json_file.stem
        # Provide friendly labels for known canonical ids
        if dataset_id == "dataset_1" or dataset_id == "global_ecommerce_sales":
            label = "Dataset 1"
            description = "Global E-Commerce Sales"
        elif dataset_id == "dataset_2" or dataset_id == "retail_supply_chain_sales":
            label = "Dataset 2"
            description = "Retail Supply Chain Sales"
        else:
            label = dataset_id
            description = ""

        datasets.append({
            "id": dataset_id,
            "label": label,
            "description": description,
            "dataPath": f"/data/datasets/{json_file.name}",
        })

    manifest = {
        "defaultDatasetId": datasets[0]["id"] if datasets else "",
        "datasets": datasets,
        "sqlAnalysis": {},
        "visualizations": [],
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest with {len(datasets)} datasets to: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
