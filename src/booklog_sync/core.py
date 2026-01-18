from pathlib import Path
import yaml
import re

BOOKLOG_CSV_COLUMNS = [
    "service_id",
    "item_id",
    "isbn13",
    "category",
    "rating",
    "status",
    "review",
    "tags",
    "memo",
    "registered_at",
    "finished_at",
    "title",
    "author",
    "publisher",
    "publish_year",
    "type",
    "page_count",
]

# ファイル名の最大バイト数。OS上の上限は255バイトだが、何かの操作でファイル名にプレフィックスがつく場合などを考慮して200バイトとする。UTF-8。
FILENAME_MAX_BYTE_LENGTH = 200


def convert_row_to_properties(row: dict[str, str]) -> dict[str, any]:
    """
    ブクログのCSVの1行をObsidianのフロントマター用辞書に変換する
    """
    rating_str: str = row.get("rating", "")
    rating = int(rating_str) if rating_str.isdigit() else None

    # TODO CSV上に値が存在しないときの処理

    return {
        "title": row.get("title"),
        "authors": [row.get("author")],
        "publisher": row.get("publisher"),
        "publish_year": row.get("publish_year"),
        "status": row.get("status"),
        "rating": rating,
    }


def _sanitize_filename(filename: str, max_bytes: int = 200) -> str:
    """
    全OSで安全なファイル名に変換する。
    スペースは保持し、禁止文字のみを '_' に置換する。
    また、Obsidianのリンクを壊さないために '[' と ']' も置換する。
    """
    invalid_chars = r'[\\/:*?"<>|\x00-\x1f\[\]]'
    sanitized = re.sub(invalid_chars, "_", filename)
    sanitized = sanitized.strip(" .")

    if not sanitized:
        sanitized = "unnamed_book"

    encoded = sanitized.encode("utf-8")
    if len(encoded) > max_bytes:
        sanitized = encoded[:max_bytes].decode("utf-8", errors="ignore")

    return sanitized


def generate_filename(
    author: str, title: str, publisher: str, publish_year: str
) -> str:
    filename_without_extension = f"{author}『{title}』（{publisher}、{publish_year}）"

    # ファイル名が長すぎる場合、ファイル名を切り詰めてから拡張子を付ける。
    # FILENAME_MAX_BYTE_LENGTHから、拡張子.mdの3バイトを除いたバイト数が拡張子なしファイル名のサイズ上限。
    encoded = filename_without_extension.encode("utf-8")
    filename_without_extension_max_byte_length = FILENAME_MAX_BYTE_LENGTH - 3
    if len(encoded) > filename_without_extension_max_byte_length:
        # ignore を指定することで、途中で切れたマルチバイト文字を破棄する。
        filename_without_extension = encoded[
            :filename_without_extension_max_byte_length
        ].decode("utf-8", errors="ignore")

    filename = f"{filename_without_extension}.md"

    sanitized = _sanitize_filename(filename)
    return sanitized


def save_book_to_markdown(
    vault_path: str, books_dir: str, properties: dict, body: str = ""
):
    """
    書籍データをMarkdownファイルとして保存する
    """
    base_path = Path(vault_path) / books_dir
    base_path.mkdir(parents=True, exist_ok=True)

    filename = generate_filename(
        properties["authors"][0],
        properties["title"],
        properties["publisher"],
        properties["publish_year"],
    )
    file_path = base_path / _sanitize_filename(filename)

    frontmatter = yaml.dump(properties, allow_unicode=True, sort_keys=False)

    content = f"---\n{frontmatter}---\n{body}\n"
    file_path.write_text(content, encoding="utf-8")

    print(f"Saved: {file_path}")
