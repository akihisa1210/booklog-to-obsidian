import pytest


def test_load_config_valid(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "csv_path: 'data.csv'\nvault_path: 'MyVault'\nbooks_dir: 'Books'",
        encoding="utf-8",
    )

    from booklog_sync.config import load_config

    config = load_config(config_file)
    assert config["csv_path"] == "data.csv"
    assert config["vault_path"] == "MyVault"
    assert config["books_dir"] == "Books"


def test_load_config_without_csv_path(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "vault_path: 'MyVault'\nbooks_dir: 'Books'", encoding="utf-8"
    )

    from booklog_sync.config import load_config

    with pytest.raises(ValueError, match="csv_path"):
        load_config(config_file)
