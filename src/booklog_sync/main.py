from pathlib import Path
import csv
import sys

from booklog_sync.config import load_config
from booklog_sync.core import (
    BOOKLOG_CSV_COLUMNS,
    convert_row_to_properties,
    save_book_to_markdown,
)


def run_sync(csv_path: Path, vault_path: Path, books_dir: str):
    """
    CSVファイルのパスを受け取り、各行のデータをマークダウンに変換する。
    """
    with open(csv_path, "r", encoding="cp932") as f:
        reader = csv.DictReader(f, fieldnames=BOOKLOG_CSV_COLUMNS)
        for row in reader:
            props = convert_row_to_properties(row)
            save_book_to_markdown(str(vault_path), books_dir, props)


def main():
    try:
        config = load_config("config.yaml")
        run_sync(
            Path(config["csv_path"]),
            Path(config["vault_path"]),
            config["books_dir"]
        )
    except Exception as e:
        print{f"エラーが発生しました: {e}"}
        sys.exit(1)
