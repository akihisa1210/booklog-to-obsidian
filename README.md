# ブクログの本棚をObsidianに同期するツール

ブクログからエクスポートしたCSVを読み込み、ObsidianのVault内に書籍ごとのMarkdownファイルを作成・更新するツールです。

## 実行方法

### 1. Pythonとuvのインストール
1. Pythonをインストールします。
2. uvをインストールします。

### 2. ツールの準備
1. このプロジェクトをクローンします。
```sh
git clone https://github.com/akihisa1210/booklog-to-obsidian.git
```

2. `uv sync` で依存関係をダウンロードします。
```sh
cd booklog-to-obsidian
uv sync
```

### 3. ブクログのCSVのダウンロード
1. ブクログの本棚ページからCSVファイルをダウンロードします。

### 4. 設定ファイルの作成
1. `config.yaml.example`をコピーして`config.yaml`を作成します。
2. 自分の環境に合わせてパスを書き換えます。
```yaml
csv_path: 'C:/path/to/your/booklog.csv' # ブクログからダウンロードしたCSVのパス
vault_path: 'C:/path/to/your/ObsidianVault' # ObsidianのVaultのパス
books_dir: 'Books' # ObsidianのVault内にある、書籍ファイルを配置するフォルダのパス
```

### 5. ツールの実行
1. ツールを実行します。
```sh
uv run scr/booklog_sync/main.py
```

## 仕様

### ファイルの作成

CSVのデータに基づき、以下の形式のファイルを作成します。

```md
---
item_id: <ブクログ上のアイテムID>
title: <書籍タイトル>
author: <著者> # 著者が複数の書籍でも、ブクログ上は一人のみが保存されている
isbn13: <ISBN> # 紙書籍のみ
publisher: <出版社名>
publish_year: <出版年>
status: <ブクログ上の読書状況>
rating: <ブクログ上の評価>
---


```

ファイル名は以下の形式になります。
```
<著者>『<書籍タイトル>』（<出版社名>、<出版年>）.md
```
- ファイル名に使用できない文字はアンダースコア（`_`）に置き換えられます。空白は保持されます。
- ファイル名の長さの上限は200バイトです。ファイル名が200バイトを超える場合、200バイト以下になるように拡張子より前の部分を切り詰めます。


### ファイルの更新

CSVのアイテムID（2列目）と`books_dir`内のファイルの`item_id`の値が一致する場合、そのファイルのフロントマターをCSVの情報で更新します。


## 開発者向け

### テスト実行
```sh
uv run pytest
```
