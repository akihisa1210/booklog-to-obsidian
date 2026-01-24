from pathlib import Path
import csv
import sys

from booklog_sync.config import load_config
from booklog_sync.core import (
    BOOKLOG_CSV_COLUMNS,
    Book,
    convert_csv,
    save_book_to_markdown,
    build_isbn13_index,
)


def run_sync(csv_path: Path, vault_path: Path, books_dir: str):
    """
    CSVファイルのパスを受け取り、各行のデータをマークダウンに変換する。
    """
    isbn13_index = build_isbn13_index(Path(vault_path) / books_dir)

    with open(csv_path, "r", encoding="cp932") as f:
        # TODO reader、rowに型を付ける
        reader = csv.DictReader(f, fieldnames=BOOKLOG_CSV_COLUMNS)
        for row in reader:
            book: Book = convert_csv(row)

            isbn13 = row.get("isbn13")
            existing_file = isbn13_index.get(isbn13)

            if existing_file:
                save_book_to_markdown(
                    str(vault_path), books_dir, book, existing_file=existing_file
                )
            else:
                save_book_to_markdown(str(vault_path), books_dir, book)


def main():
    try:
        config = load_config("config.yaml")
        run_sync(
            Path(config["csv_path"]), Path(config["vault_path"]), config["books_dir"]
        )
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
