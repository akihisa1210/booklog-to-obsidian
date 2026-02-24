import logging

from booklog_sync.main import run_sync


def test_run_sync(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "...,1000000000,9784000000001,...,5,読み終わった,...,...,...,...,...,テストタイトル,テスト作者名,テスト出版社,2020,...",
        encoding="cp932",
    )

    books_path = tmp_path / "Vault" / "Books"

    run_sync(csv_file, books_path)

    assert (
        books_path / "テスト作者名『テストタイトル』（テスト出版社、2020）.md"
    ).exists()

    created_files = list(books_path.glob("*.md"))
    assert len(created_files) == 1


def test_run_sync_existing_file(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "...,1000000000,9784000000001,...,5,読み終わった,...,...,...,...,...,タイトル,著者A,テスト出版社,2020,...",
        encoding="cp932",
    )

    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        "---\nitem_id: '1000000000'\ntitle: タイトル\nauthor: 著者A\nisbn13: '9784000000001'\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 積読\nrating:\n---\n## メモ\n面白かった",
        encoding="utf-8",
    )

    run_sync(csv_file, books_path)

    assert (books_path / "Existing_Book.md").exists()

    content = existing_file.read_text(encoding="utf-8")

    assert "item_id: '1000000000'" in content
    assert "title: タイトル" in content
    assert "author: 著者A" in content
    assert "isbn13: '9784000000001'" in content
    assert "publisher: テスト出版社" in content
    assert "publish_year: '2020'" in content
    assert "status: 読み終わった" in content
    assert "rating: 5" in content

    assert "## メモ" in content
    assert "面白かった" in content

    created_files = list(books_path.glob("*.md"))
    assert len(created_files) == 1


def test_run_sync_logs_summary(tmp_path, caplog):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "...,1000000000,9784000000001,...,5,読み終わった,...,...,...,...,...,テストタイトル,テスト作者名,テスト出版社,2020,...",
        encoding="cp932",
    )

    books_path = tmp_path / "Vault" / "Books"

    with caplog.at_level(logging.INFO, logger="booklog_sync.main"):
        run_sync(csv_file, books_path)

    assert "Sync completed: 1 created, 0 updated, 0 unchanged" in caplog.text
