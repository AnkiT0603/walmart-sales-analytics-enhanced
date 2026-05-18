from pathlib import Path
from urllib.request import urlretrieve

from src.config import RAW_DATA_PATH, WALMART_DATASET_URL


def download_dataset(output_path: Path = RAW_DATA_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(WALMART_DATASET_URL, output_path)
    return output_path


if __name__ == "__main__":
    path = download_dataset()
    print(f"Downloaded Walmart dataset to {path}")
