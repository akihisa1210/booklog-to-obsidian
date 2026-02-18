# CLAUDE.md

## プロジェクト概要

ブクログCSVをObsidianのMarkdownファイルに同期するCLIツール。

## コマンド

- テスト実行: `uv run pytest tests/ -v`
- 同期実行: `uv run booklog-sync sync --config config.yaml`
- 監視実行: `uv run booklog-sync watch --config config.yaml`

## プロジェクト構成

- `src/booklog_sync/` - メインソースコード
  - `main.py` - CLI定義と`run_sync()`
  - `core.py` - CSV変換、差分検出、Markdown書き出し
  - `config.py` - YAML設定ファイルの読み込み（`SyncConfig` dataclass）
  - `watcher.py` - watchdogによるCSVファイル監視
- `tests/` - テストコード（pytest）

## コーディング規約

- 言語: Python 3.13+
- 型付け: `TypedDict`（`Book`, `BooklogCSVRow`）、`Optional`を使用
- ログ: `logging`モジュールを使用（`print()`ではなく`logger.info()`/`logger.debug()`）
- CSVエンコーディング: `cp932`（ブクログのエクスポート形式）
- YAML: `pyyaml`の`yaml.dump(allow_unicode=True, sort_keys=False)`で出力
- テスト: ヘルパー関数`create_book()`/`create_booklog_csv_row()`でテストデータを生成
