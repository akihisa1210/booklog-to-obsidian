def test_run_sync(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "...,...,9784000000001,...,5,読み終わった,...,...,...,...,...,テストタイトル,テスト作者名,テスト出版社,2020,...",
        encoding="cp932",
    )

    vault_path = tmp_path / "Vault"

    from booklog_sync.main import run_sync

    run_sync(csv_file, vault_path, "Books")

    assert (
        vault_path / "Books" / "テスト作者名『テストタイトル』（テスト出版社、2020）.md"
    ).exists()

    created_files = list((vault_path / "Books").glob("*.md"))
    assert len(created_files) == 1


def test_run_sync_existing_file(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "...,...,9784000000001,...,5,読み終わった,...,...,...,...,...,タイトル,著者A,テスト出版社,2020,...",
        encoding="cp932",
    )

    vault_path = tmp_path / "Vault"
    books_dir = "Books"
    (vault_path / books_dir).mkdir(parents=True)

    existing_file = vault_path / books_dir / "Existing_Book.md"
    existing_file.write_text(
        "---\ntitle: タイトル\nauthors:\n- 著者A\nisbn13: 9784000000001\npublisher: テスト出版社\npublish_year: '2020'\nstatus: 積読\nrating:\n---\n## メモ\n面白かった",
        encoding="utf-8",
    )

    from booklog_sync.main import run_sync

    run_sync(csv_file, vault_path, "Books")

    assert (vault_path / "Books" / "Existing_Book.md").exists()

    content = existing_file.read_text(encoding="utf-8")

    assert "title: タイトル" in content
    assert "authors:\n- 著者A" in content
    assert "isbn13: '9784000000001'" in content
    assert "publisher: テスト出版社" in content
    assert "publish_year: '2020'" in content
    assert "status: 読み終わった" in content
    assert "rating: 5" in content

    assert "## メモ" in content
    assert "面白かった" in content

    created_files = list((vault_path / "Books").glob("*.md"))
    assert len(created_files) == 1
