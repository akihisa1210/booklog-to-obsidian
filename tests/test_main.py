def test_run_sync(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "...,...,...,...,5,読み終わった,...,...,...,...,...,テストタイトル,テスト作者名,テスト出版社,2020,...",
        encoding="cp932",
    )

    vault_path = tmp_path / "MyVault"

    from booklog_sync.main import run_sync

    run_sync(csv_file, vault_path, "Books")

    assert (
        vault_path / "Books" / "テスト作者名『テストタイトル』（テスト出版社、2020）.md"
    ).exists()
