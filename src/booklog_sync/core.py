from pathlib import Path
import yaml

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


def save_book_to_markdown(
    vault_path: str, books_dir: str, properties: dict, body: str = ""
):
    """
    書籍データをMarkdownファイルとして保存する
    """
    base_path = Path(vault_path) / books_dir
    base_path.mkdir(parents=True, exist_ok=True)

    # TODO ファイル名に使えない文字の処理
    filename = f"{properties['authors'][0]}『{properties['title']}』（{properties['publisher']}、{properties['publish_year']}）.md"
    file_path = base_path / filename

    frontmatter = yaml.dump(properties, allow_unicode=True, sort_keys=False)

    content = f"---\n{frontmatter}---\n{body}\n"
    file_path.write_text(content, encoding="utf-8")

    print(f"Saved: {file_path}")
