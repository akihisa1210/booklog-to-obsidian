def test_convert_row_to_properties():
    from booklog_sync.core import convert_row_to_properties

    row = {
        "title": "テストタイトル",
        "author": "テスト作者名",
        "status": "読み終わった",
        "rating": "5",
    }

    props = convert_row_to_properties(row)

    assert props["title"] == "テストタイトル"
    assert props["authors"] == ["テスト作者名"]
    assert props["status"] == "読み終わった"
    assert props["rating"] == 5


def test_convert_row_to_properties_without_rating():
    from booklog_sync.core import convert_row_to_properties

    row = {
        "title": "テストタイトル",
        "author": "テスト作者名",
        "status": "読み終わった",
        "rating": "",
    }

    props = convert_row_to_properties(row)

    assert props["title"] == "テストタイトル"
    assert props["authors"] == ["テスト作者名"]
    assert props["status"] == "読み終わった"
    assert props["rating"] == 0


# def test_save_book_to_markdown(tmp_path):
#     vault_path = tmp_path / "MyVault"
#     books_dir = "Books"
#     props = {
#         "title": "テストタイトル",
#         "authors": ["テスト作者名"],
#         "status": "読み終わった",
#         "rating": 5,
#     }
#     body = "# 感想\n面白かった"

#     save_book_to_markdown(str(vault_path), books_dir, props, body)

#     expected_file = vault_path / books_dir / "テスト作者名『テストタイトル』.md"
