import pytest
from pathlib import Path


def test_load_config_valid(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "csv_path: 'data.csv'\nbooks_path: 'MyVault/Books'",
        encoding="utf-8",
    )

    from booklog_sync.config import load_config

    config = load_config(config_file)
    assert config.csv_path == Path("data.csv")
    assert config.books_path == Path("MyVault/Books")


def test_load_config_without_csv_path(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "books_path: 'MyVault/Books'", encoding="utf-8"
    )

    from booklog_sync.config import load_config

    with pytest.raises(ValueError, match="csv_path"):
        load_config(config_file)


def test_load_config_without_books_path(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "csv_path: 'data.csv'", encoding="utf-8"
    )

    from booklog_sync.config import load_config

    with pytest.raises(ValueError, match="books_path"):
        load_config(config_file)
