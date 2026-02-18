from pathlib import Path
import csv
import logging
import sys

from booklog_sync.config import load_config
from booklog_sync.core import (
    BOOKLOG_CSV_COLUMNS,
    Book,
    convert_csv,
    save_book_to_markdown,
    build_id_book_index,
)

logger = logging.getLogger(__name__)


def run_sync(csv_path: Path, books_path: Path):
    """
    CSVファイルのパスを受け取り、ファイルを作成または更新する。
    """
    id_book_index = build_id_book_index(books_path)
    logger.debug("id_book_index: %s", id_book_index)

    with open(csv_path, "r", encoding="cp932") as f:
        reader = csv.DictReader(f, fieldnames=BOOKLOG_CSV_COLUMNS)
        for row in reader:
            book: Book = convert_csv(row)

            item_id = row.get("item_id")
            existing_file = id_book_index.get(item_id)

            if existing_file:
                save_book_to_markdown(
                    books_path, book, existing_file=existing_file
                )
            else:
                save_book_to_markdown(books_path, book)


def main():
    import argparse

    config_parser = argparse.ArgumentParser(add_help=False)
    config_parser.add_argument(
        "--config", default="config.yaml", help="設定ファイルのパス (デフォルト: config.yaml)"
    )

    parser = argparse.ArgumentParser(
        description="ブクログCSVをObsidianに同期するツール",
        parents=[config_parser],
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("sync", parents=[config_parser], help="CSVファイルを読み込み同期を実行する")

    subparsers.add_parser("watch", parents=[config_parser], help="CSVファイルを監視し、変更時に自動同期する")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    try:
        config = load_config(args.config)

        if args.command == "watch":
            from booklog_sync.watcher import start_watching

            # 初回同期
            run_sync(config.csv_path, config.books_path)
            start_watching(config.csv_path, config.books_path)
        else:
            # デフォルト: sync
            run_sync(config.csv_path, config.books_path)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
