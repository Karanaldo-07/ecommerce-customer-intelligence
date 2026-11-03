"""Download the official UCI Online Retail II workbook.

Run from the repository root:
    python scripts/download_data.py

The raw workbook is stored under data/raw/ and must not be committed to Git.
"""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import requests

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
TARGET = RAW_DIR / "online_retail_II.xlsx"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        print(f"Dataset already exists: {TARGET}")
        return

    print("Downloading Online Retail II from the official UCI repository...")
    response = requests.get(URL, timeout=(30, 180))
    response.raise_for_status()

    with ZipFile(BytesIO(response.content)) as archive:
        candidates = [
            name for name in archive.namelist()
            if name.lower().endswith((".xlsx", ".xls"))
        ]
        if not candidates:
            raise RuntimeError(
                f"No Excel workbook found in archive. Files: {archive.namelist()}"
            )
        # The official archive contains the workbook; choose the largest Excel file.
        selected = max(candidates, key=lambda name: archive.getinfo(name).file_size)
        TARGET.write_bytes(archive.read(selected))

    print(f"Downloaded {TARGET} ({TARGET.stat().st_size:,} bytes)")
    print("Next: inspect workbook sheets and validate the source columns.")


if __name__ == "__main__":
    main()
