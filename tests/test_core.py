from conftest import create_book, create_booklog_csv_row

from booklog_sync.core import (
    _sanitize_filename,
    build_id_book_index,
    convert_csv,
    diff_frontmatter,
    generate_filename,
    save_book_to_markdown,
)


def test_convert_row_to_properties():
    row = create_booklog_csv_row()

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
    books_path = tmp_path / "MyVault" / "Books"
    book = create_book()
    body = "# 感想\n面白かった"

    save_book_to_markdown(books_path, book, body)

    expected_file = (
        books_path
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
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    existing_file = books_path / "Existing_Book.md"
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
        books_path, updated_book_data, existing_file=existing_file
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


def test_save_book_with_triple_dash_in_title(tmp_path):
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    book = create_book({"title": "タイトル---サブタイトル"})
    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        "---\nitem_id: '1000000000'\ntitle: タイトル---サブタイトル\nauthor: テスト作者名\nisbn13: '9784000000001'\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 読み終わった\nrating: 5\n---\n## メモ\n面白かった",
        encoding="utf-8",
    )

    result = save_book_to_markdown(books_path, book, existing_file=existing_file)

    assert result == "unchanged"


def test_sanitize_filename():
    filename = " /a "

    assert _sanitize_filename(filename) == "_a"


def test_generate_filename():
    title = generate_filename("テスト作者名", "テストタイトル", "テスト出版社", "2020")
    assert title == "テスト作者名『テストタイトル』（テスト出版社、2020）.md"


def test_generate_filename_long():
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

    index = build_id_book_index(books_dir)

    assert index["1000000000"] == file1
    assert "1000000000" in index
    assert len(index) == 1


def test_diff_frontmatter_no_changes():
    book = create_book()
    existing_props = {
        "item_id": "1000000000",
        "title": "テストタイトル",
        "author": "テスト作者名",
        "isbn13": "9784000000001",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": 5,
    }

    changes = diff_frontmatter(existing_props, book)

    assert changes == {}


def test_diff_frontmatter_with_changes():
    book = create_book({"rating": 3})
    existing_props = {
        "item_id": "1000000000",
        "title": "テストタイトル",
        "author": "テスト作者名",
        "isbn13": "9784000000001",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": 5,
    }

    changes = diff_frontmatter(existing_props, book)

    assert changes == {"rating": (5, 3)}


def test_diff_frontmatter_multiple_changes():
    book = create_book({"rating": 3, "status": "積読", "title": "新タイトル"})
    existing_props = {
        "item_id": "1000000000",
        "title": "テストタイトル",
        "author": "テスト作者名",
        "isbn13": "9784000000001",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": 5,
    }

    changes = diff_frontmatter(existing_props, book)

    assert changes == {
        "title": ("テストタイトル", "新タイトル"),
        "status": ("読み終わった", "積読"),
        "rating": (5, 3),
    }


def test_diff_frontmatter_rating_none_to_int():
    book = create_book({"rating": 5})
    existing_props = {
        "item_id": "1000000000",
        "title": "テストタイトル",
        "author": "テスト作者名",
        "isbn13": "9784000000001",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": None,
    }

    changes = diff_frontmatter(existing_props, book)

    assert changes == {"rating": (None, 5)}


def test_diff_frontmatter_rating_int_to_none():
    book = create_book({"rating": None})
    existing_props = {
        "item_id": "1000000000",
        "title": "テストタイトル",
        "author": "テスト作者名",
        "isbn13": "9784000000001",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": 5,
    }

    changes = diff_frontmatter(existing_props, book)

    assert changes == {"rating": (5, None)}


def test_save_book_unchanged_skips_write(tmp_path):
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    book = create_book()
    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        "---\nitem_id: '1000000000'\ntitle: テストタイトル\nauthor: テスト作者名\nisbn13: '9784000000001'\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 読み終わった\nrating: 5\n---\n## メモ\n面白かった",
        encoding="utf-8",
    )

    mtime_before = existing_file.stat().st_mtime

    result = save_book_to_markdown(books_path, book, existing_file=existing_file)

    mtime_after = existing_file.stat().st_mtime

    assert result == "unchanged"
    assert mtime_before == mtime_after


def test_save_book_updated_returns_updated(tmp_path):
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    book = create_book({"rating": 3})
    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        "---\nitem_id: '1000000000'\ntitle: テストタイトル\nauthor: テスト作者名\nisbn13: '9784000000001'\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 読み終わった\nrating: 5\n---\n## メモ\n面白かった",
        encoding="utf-8",
    )

    result = save_book_to_markdown(books_path, book, existing_file=existing_file)

    assert result == "updated"


def test_save_book_update_does_not_add_extra_newline(tmp_path):
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        "---\nitem_id: '1000000000'\ntitle: テストタイトル\nauthor: テスト作者名\nisbn13: '9784000000001'\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 積読\nrating: 5\n---\n## メモ\n面白かった",
        encoding="utf-8",
    )

    # 1回目の更新
    book1 = create_book({"status": "読み終わった"})
    save_book_to_markdown(books_path, book1, existing_file=existing_file)
    content_after_first = existing_file.read_text(encoding="utf-8")

    # 2回目の更新
    book2 = create_book({"status": "積読"})
    save_book_to_markdown(books_path, book2, existing_file=existing_file)
    content_after_second = existing_file.read_text(encoding="utf-8")

    # フロントマターと本文の間の空行数が増えていないことを確認
    assert content_after_first.count("\n---\n") == 1
    assert content_after_second.count("\n---\n") == 1


def test_save_book_created_returns_created(tmp_path):
    books_path = tmp_path / "Vault" / "Books"
    book = create_book()

    result = save_book_to_markdown(books_path, book)

    assert result == "created"


def test_save_book_unchanged_preserves_body(tmp_path):
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    book = create_book()
    body_text = "\n## メモ\n面白かった"
    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        f"---\nitem_id: '1000000000'\ntitle: テストタイトル\nauthor: テスト作者名\nisbn13: '9784000000001'\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 読み終わった\nrating: 5\n---{body_text}",
        encoding="utf-8",
    )

    save_book_to_markdown(books_path, book, existing_file=existing_file)

    content = existing_file.read_text(encoding="utf-8")

    assert "## メモ" in content
    assert "面白かった" in content


def test_save_book_yaml_parse_error_overwrites(tmp_path):
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    book = create_book()
    existing_file = books_path / "Broken.md"
    existing_file.write_text(
        "---\nitem_id: '1000000000'\ntitle: [invalid yaml\n---\n## メモ\n",
        encoding="utf-8",
    )

    result = save_book_to_markdown(books_path, book, existing_file=existing_file)

    assert result == "updated"

    content = existing_file.read_text(encoding="utf-8")
    assert "title: テストタイトル" in content
    assert "## メモ" in content


def test_build_id_book_index_when_item_id_is_not_a_number(tmp_path):
    books_dir = tmp_path / "Books"
    books_dir.mkdir()

    # item_idを持つファイル
    file1 = books_dir / "Book1.md"
    file1.write_text("---\ntags:\nitem_id: B0D143YRBP\n---", encoding="utf-8")

    # item_idを持たないファイル
    file2 = books_dir / "Note.md"
    file2.write_text("# メモ\nitem_idなし", encoding="utf-8")

    index = build_id_book_index(books_dir)

    assert index["B0D143YRBP"] == file1
    assert "B0D143YRBP" in index
    assert len(index) == 1
