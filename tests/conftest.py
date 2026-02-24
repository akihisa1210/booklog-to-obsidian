from booklog_sync.core import Book, BooklogCSVRow


def create_booklog_csv_row(props: dict[str, str] | None = None) -> BooklogCSVRow:
    if props is None:
        props = {}

    default_csv_row: BooklogCSVRow = {
        "item_id": "1000000000",
        "title": "テストタイトル",
        "author": "テスト作者名",
        "isbn13": "9784000000001",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": "5",
    }

    return {**default_csv_row, **props}


def create_book(props: dict[str, str] | None = None) -> Book:
    if props is None:
        props = {}

    default_book: Book = {
        "item_id": "1000000000",
        "title": "テストタイトル",
        "author": "テスト作者名",
        "isbn13": "9784000000001",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": 5,
    }

    return {**default_book, **props}
