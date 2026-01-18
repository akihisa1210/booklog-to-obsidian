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
    rating: int = 0
    rating_str: str = row.get("rating", "")
    if rating_str.isdigit():
        rating = int(rating_str)

    return {
        "title": row.get("title"),
        "authors": [row.get("author")],
        "status": row.get("status"),
        "rating": rating,
    }
