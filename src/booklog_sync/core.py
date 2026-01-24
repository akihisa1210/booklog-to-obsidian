from pathlib import Path
import yaml
import re
from typing import Final, TypedDict, Optional, get_type_hints


class BooklogCSVRow(TypedDict, total=False):
    service_id: str
    item_id: str
    isbn13: str
    category: str
    rating: str
    status: str
    review: str
    tags: str
    memo: str
    registered_at: str
    finished_at: str
    title: str
    author: str
    publisher: str
    publish_year: str
    book_type: str
    page_count: str


BOOKLOG_CSV_COLUMNS: Final = list(get_type_hints(BooklogCSVRow).keys())


class Book(TypedDict):
    title: str
    authors: list[str]
    isbn13: Optional[str]
    publisher: Optional[str]
    publish_year: Optional[str]
    status: Optional[str]
    rating: Optional[int]


# ファイル名の最大バイト数。OS上の上限は255バイトだが、何かの操作でファイル名にプレフィックスがつく場合などを考慮して200バイトとする。UTF-8。
FILENAME_MAX_BYTE_LENGTH: Final = 200


def convert_csv(row: BooklogCSVRow) -> Book:
    """
    ブクログのCSVの1行をObsidianのフロントマター用書籍データに変換する
    """
    rating_str: str = row.get("rating", "")
    rating = int(rating_str) if rating_str.isdigit() else None

    return {
        "title": row.get("title"),
        "authors": [row.get("author")],
        "isbn13": row.get("isbn13"),
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


def build_isbn13_index(books_dir: Path) -> dict[str, Path]:
    """
    ディレクトリ内の全ファイルを走査し、{13桁ISBN: Path} の辞書を返す
    """
    index = {}
    if not books_dir.exists():
        return index

    for file_path in books_dir.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        match = re.search(r'^isbn13:\s*["\']?(\d+)["\']?', content, re.MULTILINE)
        if match:
            isbn13 = match.group(1)
            index[isbn13] = file_path

    return index


def save_book_to_markdown(
    vault_path: str,
    books_dir: str,
    book: Book,
    body: str = "",
    existing_file: Path = None,
):
    """
    書籍データをMarkdownファイルとして保存する
    """

    if existing_file and existing_file.exists():
        old_content = existing_file.read_text(encoding="utf-8")
        parts = old_content.split("---", 2)

        if len(parts) >= 3:
            old_props = yaml.safe_load(parts[1]) or {}
            old_props.update(book)
            content = f"---\n{yaml.dump(old_props, allow_unicode=True, sort_keys=False)}---\n{parts[2]}"
            existing_file.write_text(content, encoding="utf-8")
            print(f"Updated: {existing_file}")
            return

    base_path = Path(vault_path) / books_dir
    # TODO ディレクトリ作成は初回の1回だけで十分
    base_path.mkdir(parents=True, exist_ok=True)

    filename = generate_filename(
        book["authors"][0],
        book["title"],
        book["publisher"],
        book["publish_year"],
    )
    file_path = base_path / _sanitize_filename(filename)

    frontmatter = yaml.dump(book, allow_unicode=True, sort_keys=False)

    content = f"---\n{frontmatter}---\n{body}\n"
    file_path.write_text(content, encoding="utf-8")

    print(f"Saved: {file_path}")
    return
