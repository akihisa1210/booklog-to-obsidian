def test_convert_row_to_properties():
    from booklog_sync.core import convert_row_to_properties

    row = {
        "title": "テストタイトル",
        "author": "テスト作者名",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": "5",
    }

    props = convert_row_to_properties(row)

    assert props["title"] == "テストタイトル"
    assert props["authors"] == ["テスト作者名"]
    assert props["publisher"] == "テスト出版社"
    assert props["publish_year"] == "2020"
    assert props["status"] == "読み終わった"
    assert props["rating"] == 5


def test_convert_row_to_properties_without_rating():
    from booklog_sync.core import convert_row_to_properties

    row = {
        "title": "テストタイトル",
        "author": "テスト作者名",
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": "",
    }

    props = convert_row_to_properties(row)

    assert props["title"] == "テストタイトル"
    assert props["authors"] == ["テスト作者名"]
    assert props["publisher"] == "テスト出版社"
    assert props["publish_year"] == "2020"
    assert props["status"] == "読み終わった"
    assert props["rating"] is None


def test_save_book_to_markdown(tmp_path):
    from booklog_sync.core import save_book_to_markdown

    vault_path = tmp_path / "MyVault"
    books_dir = "Books"
    props = {
        "title": "テストタイトル",
        "authors": ["テスト作者名"],
        "publisher": "テスト出版社",
        "publish_year": "2020",
        "status": "読み終わった",
        "rating": 5,
    }
    body = "# 感想\n面白かった"

    save_book_to_markdown(str(vault_path), books_dir, props, body)

    expected_file = (
        vault_path
        / books_dir
        / "テスト作者名『テストタイトル』（テスト出版社、2020）.md"
    )

    assert expected_file.exists()

    expected_content = """---
title: テストタイトル
authors:
- テスト作者名
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
