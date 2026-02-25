import subprocess
import sys
from pathlib import Path

import yaml


def run_booklog_sync(config_file: Path, debug: bool = True) -> subprocess.CompletedProcess:
    """booklog-sync sync コマンドを subprocess で実行する。"""
    cmd = [sys.executable, "-m", "booklog_sync.main", "sync", "--config", str(config_file)]
    if debug:
        cmd.append("--debug")
    return subprocess.run(cmd, capture_output=True, text=True)


def write_csv(path: Path, rows: list[str]):
    """cp932エンコーディングでCSVファイルを書き出す。"""
    path.write_text("\n".join(rows), encoding="cp932")


def write_config(tmp_path: Path, csv_path: Path, books_path: Path) -> Path:
    """config.yaml を生成して返す。"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.dump(
            {"csv_path": str(csv_path), "books_path": str(books_path)},
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return config_file


def print_preconditions(csv_path: Path, books_path: Path):
    """事前状態（CSV・既存 .md ファイル）を出力する。"""
    print("\n=== Input CSV ===")
    print(csv_path.read_text(encoding="cp932"))
    if books_path.exists():
        for md_file in sorted(books_path.glob("*.md")):
            print(f"\n=== Existing: {md_file.name} ===")
            print(md_file.read_text(encoding="utf-8"))
    else:
        print("\n(no existing .md files)")


def print_result(result: subprocess.CompletedProcess, books_path: Path):
    """CLI の stderr と生成ファイルの内容を出力する。"""
    print("\n=== CLI stderr ===")
    print(result.stderr)
    for md_file in sorted(books_path.glob("*.md")):
        print(f"\n=== Result: {md_file.name} ===")
        print(md_file.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# テストケース
# ---------------------------------------------------------------------------


def test_e2e_sync_create(tmp_path):
    """新規ファイル作成"""
    csv_path = tmp_path / "booklog.csv"
    books_path = tmp_path / "Vault" / "Books"

    write_csv(csv_path, [
        "...,1000000000,9784000000001,...,5,読み終わった,...,...,...,...,...,テストタイトル,テスト作者名,テスト出版社,2020,...",
    ])
    config_file = write_config(tmp_path, csv_path, books_path)
    print_preconditions(csv_path, books_path)

    result = run_booklog_sync(config_file)
    print_result(result, books_path)

    assert result.returncode == 0, f"Exit code != 0\nstderr:\n{result.stderr}"

    expected_file = books_path / "テスト作者名『テストタイトル』（テスト出版社、2020）.md"
    assert expected_file.exists(), f"File not created\nstderr:\n{result.stderr}"

    content = expected_file.read_text(encoding="utf-8")
    assert "item_id: '1000000000'" in content
    assert "title: テストタイトル" in content
    assert "author: テスト作者名" in content
    assert "isbn13: '9784000000001'" in content
    assert "publisher: テスト出版社" in content
    assert "publish_year: '2020'" in content
    assert "status: 読み終わった" in content
    assert "rating: 5" in content

    assert "Created:" in result.stderr, f"Missing 'Created:' in stderr\nstderr:\n{result.stderr}"
    assert "Sync completed: 1 created, 0 updated, 0 unchanged" in result.stderr


def test_e2e_sync_update(tmp_path):
    """既存ファイル更新"""
    csv_path = tmp_path / "booklog.csv"
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    # 既存ファイル: status=積読, rating=なし
    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        "---\n"
        "item_id: '1000000000'\n"
        "title: タイトル\n"
        "author: 著者A\n"
        "isbn13: '9784000000001'\n"
        "publisher: テスト出版社\n"
        "publish_year: '2020'\n"
        "status: 積読\n"
        "rating:\n"
        "---\n"
        "## メモ\n面白かった\n",
        encoding="utf-8",
    )

    # CSV: status=読み終わった, rating=5
    write_csv(csv_path, [
        "...,1000000000,9784000000001,...,5,読み終わった,...,...,...,...,...,タイトル,著者A,テスト出版社,2020,...",
    ])
    config_file = write_config(tmp_path, csv_path, books_path)
    print_preconditions(csv_path, books_path)

    result = run_booklog_sync(config_file)
    print_result(result, books_path)

    assert result.returncode == 0, f"Exit code != 0\nstderr:\n{result.stderr}"

    content = existing_file.read_text(encoding="utf-8")
    assert "status: 読み終わった" in content
    assert "rating: 5" in content
    assert "## メモ" in content, f"Body lost\nstderr:\n{result.stderr}"
    assert "面白かった" in content

    assert "Changes detected in" in result.stderr, f"Missing diff log\nstderr:\n{result.stderr}"


def test_e2e_sync_unchanged(tmp_path):
    """変更なしスキップ"""
    csv_path = tmp_path / "booklog.csv"
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    # 既存ファイルとCSVが一致
    existing_file = books_path / "Existing_Book.md"
    existing_file.write_text(
        "---\n"
        "item_id: '1000000000'\n"
        "title: テストタイトル\n"
        "author: テスト作者名\n"
        "isbn13: '9784000000001'\n"
        "publisher: テスト出版社\n"
        "publish_year: '2020'\n"
        "status: 読み終わった\n"
        "rating: 5\n"
        "---\n",
        encoding="utf-8",
    )

    write_csv(csv_path, [
        "...,1000000000,9784000000001,...,5,読み終わった,...,...,...,...,...,テストタイトル,テスト作者名,テスト出版社,2020,...",
    ])
    config_file = write_config(tmp_path, csv_path, books_path)
    print_preconditions(csv_path, books_path)

    result = run_booklog_sync(config_file)
    print_result(result, books_path)

    assert result.returncode == 0, f"Exit code != 0\nstderr:\n{result.stderr}"
    assert "Sync completed: 0 created, 0 updated, 1 unchanged" in result.stderr


def test_e2e_sync_multiple_books(tmp_path):
    """複数冊混在: 新規1 + 更新1 + 変更なし1"""
    csv_path = tmp_path / "booklog.csv"
    books_path = tmp_path / "Vault" / "Books"
    books_path.mkdir(parents=True)

    # 更新対象: rating なし → 5
    update_file = books_path / "Update_Book.md"
    update_file.write_text(
        "---\n"
        "item_id: '2000000000'\n"
        "title: 更新タイトル\n"
        "author: 著者B\n"
        "isbn13: '9784000000002'\n"
        "publisher: 出版社B\n"
        "publish_year: '2021'\n"
        "status: 読み終わった\n"
        "rating:\n"
        "---\n",
        encoding="utf-8",
    )

    # 変更なし
    unchanged_file = books_path / "Unchanged_Book.md"
    unchanged_file.write_text(
        "---\n"
        "item_id: '3000000000'\n"
        "title: 変更なしタイトル\n"
        "author: 著者C\n"
        "isbn13: '9784000000003'\n"
        "publisher: 出版社C\n"
        "publish_year: '2022'\n"
        "status: 読み終わった\n"
        "rating: 4\n"
        "---\n",
        encoding="utf-8",
    )

    # CSV: 新規1冊 + 更新1冊 + 変更なし1冊
    write_csv(csv_path, [
        "...,1000000000,9784000000001,...,5,読み終わった,...,...,...,...,...,新規タイトル,著者A,出版社A,2020,...",
        "...,2000000000,9784000000002,...,5,読み終わった,...,...,...,...,...,更新タイトル,著者B,出版社B,2021,...",
        "...,3000000000,9784000000003,...,4,読み終わった,...,...,...,...,...,変更なしタイトル,著者C,出版社C,2022,...",
    ])
    config_file = write_config(tmp_path, csv_path, books_path)
    print_preconditions(csv_path, books_path)

    result = run_booklog_sync(config_file)
    print_result(result, books_path)

    assert result.returncode == 0, f"Exit code != 0\nstderr:\n{result.stderr}"
    assert "Sync completed: 1 created, 1 updated, 1 unchanged" in result.stderr

    # 新規ファイルが生成されている
    new_file = books_path / "著者A『新規タイトル』（出版社A、2020）.md"
    assert new_file.exists(), f"New file not created\nstderr:\n{result.stderr}"

    # 更新ファイルの rating が更新されている
    update_content = update_file.read_text(encoding="utf-8")
    assert "rating: 5" in update_content

    # 変更なしファイルはそのまま
    unchanged_content = unchanged_file.read_text(encoding="utf-8")
    assert "rating: 4" in unchanged_content
