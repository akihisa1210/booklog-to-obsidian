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


def test_convert_row_to_properties():
    row = create_booklog_csv_row()

    from booklog_sync.core import convert_csv

    book = convert_csv(row)

    assert book["item_id"] == "1000000000"
    assert book["title"] == "テストタイトル"
    assert book["author"] == "テスト作者名"
    assert book["isbn13"] == "9784000000001"
    assert book["publisher"] == "テスト出版社"
    assert book["publish_year"] == "2020"
    assert book["status"] == "読み終わった"
    assert book["rating"] == 5


def test_convert_row_to_properties_without_rating():
    row = create_booklog_csv_row({"rating": ""})

    from booklog_sync.core import convert_csv

    book = convert_csv(row)

    assert book["item_id"] == "1000000000"
    assert book["title"] == "テストタイトル"
    assert book["author"] == "テスト作者名"
    assert book["isbn13"] == "9784000000001"
    assert book["publisher"] == "テスト出版社"
    assert book["publish_year"] == "2020"
    assert book["status"] == "読み終わった"
    assert book["rating"] is None


def test_save_book_to_markdown(tmp_path):
    from booklog_sync.core import save_book_to_markdown

    vault_path = tmp_path / "MyVault"
    books_dir = "Books"
    book = create_book()
    body = "# 感想\n面白かった"

    save_book_to_markdown(str(vault_path), books_dir, book, body)

    expected_file = (
        vault_path
        / books_dir
        / "テスト作者名『テストタイトル』（テスト出版社、2020）.md"
    )

    assert expected_file.exists()

    expected_content = """---
item_id: '1000000000'
title: テストタイトル
author: テスト作者名
isbn13: '9784000000001'
publisher: テスト出版社
publish_year: '2020'
status: 読み終わった
rating: 5
---
# 感想
面白かった
"""

    actual_content = expected_file.read_text(encoding="utf-8")

    assert actual_content == expected_content


def test_save_book_merge_existing_file(tmp_path):
    from booklog_sync.core import save_book_to_markdown

    vault_path = tmp_path / "Vault"
    books_dir = "Books"
    (vault_path / books_dir).mkdir(parents=True)

    existing_file = vault_path / books_dir / "Existing_Book.md"
    existing_file.write_text(
        "---\nitem_id: '1000000000'\ntitle: 旧タイトル\nauthors: 著者A\nisbn13: 9784000000001\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 積読\nrating:\n---\n## メモ\n面白かった",
        encoding="utf-8",
    )

    updated_book_data = create_book(
        {
            "title": "新タイトル",
            "author": "著者B",
            "status": "読み終わった",
            "rating": 5,
        }
    )

    save_book_to_markdown(
        str(vault_path), books_dir, updated_book_data, existing_file=existing_file
    )

    content = existing_file.read_text(encoding="utf-8")

    assert "item_id: '1000000000'" in content
    assert "title: 新タイトル" in content
    assert "author: 著者B" in content
    assert "isbn13: '9784000000001'" in content
    assert "publisher: テスト出版社" in content
    assert "publish_year: '2020'" in content
    assert "status: 読み終わった" in content
    assert "rating: 5" in content

    assert "## メモ" in content
    assert "面白かった" in content


def test_sanitize_filename():
    filename = " /a "

    from booklog_sync.core import _sanitize_filename

    assert _sanitize_filename(filename) == "_a"


def test_generate_filename():
    from booklog_sync.core import generate_filename

    title = generate_filename("テスト作者名", "テストタイトル", "テスト出版社", "2020")
    assert title == "テスト作者名『テストタイトル』（テスト出版社、2020）.md"


def test_generate_filename_long():
    from booklog_sync.core import generate_filename

    # 作者名、タイトル、出版社、出版年をファイル名のフォーマットに合わせて結合すると198バイトになるテストデータ。
    # 拡張.mdを付けると201バイトとなり、このツールのファイル名文字数上限の200バイトを超えてしまう。
    title = generate_filename(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "a",
        "a",
        "2020",
    )
    assert (
        title
        == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa『a』（a、2020.md"
    )


def test_build_id_book_index(tmp_path):
    books_dir = tmp_path / "Books"
    books_dir.mkdir()

    # item_idを持つファイル
    file1 = books_dir / "Book1.md"
    file1.write_text("---\nitem_id: 1000000000\n---", encoding="utf-8")

    # item_idを持たないファイル
    file2 = books_dir / "Note.md"
    file2.write_text("# メモ\nitem_idなし", encoding="utf-8")

    from booklog_sync.core import build_id_book_index

    index = build_id_book_index(books_dir)

    assert index["1000000000"] == file1
    assert "1000000000" in index
    assert len(index) == 1


def test_build_id_book_index_when_item_id_is_not_a_number(tmp_path):
    books_dir = tmp_path / "Books"
    books_dir.mkdir()

    # item_idを持つファイル
    file1 = books_dir / "Book1.md"
    file1.write_text("---\ntags:\nitem_id: B0D143YRBP\n---", encoding="utf-8")

    # item_idを持たないファイル
    file2 = books_dir / "Note.md"
    file2.write_text("# メモ\nitem_idなし", encoding="utf-8")

    from booklog_sync.core import build_id_book_index

    index = build_id_book_index(books_dir)

    assert index["B0D143YRBP"] == file1
    assert "B0D143YRBP" in index
    assert len(index) == 1
