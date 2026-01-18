import yaml
from pathlib import Path


def load_config(config_path: str | Path) -> dict:
    """
    設定ファイルを読み込み、必要な項目がそろっているかチェックする
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    required_keys = ["csv_path", "vault_path", "books_dir"]
    for key in required_keys:
        if key not in config or not config[key]:
            raise ValueError(f"設定エラー: '{key}' は必須項目です。")

    return config
