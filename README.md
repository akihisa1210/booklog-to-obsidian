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
books_path: 'C:/path/to/your/ObsidianVault/Books' # 書籍ファイルを配置するフォルダの絶対パス
```

### 5. ツールの実行

#### 手動同期（1回だけ実行）
```sh
uv run booklog-sync sync --config config.yaml
```

#### ファイル監視モード（CSVの変更を自動検知して同期）
```sh
uv run booklog-sync watch --config config.yaml
```
`--config` を省略するとカレントディレクトリの `config.yaml` が使われます。

## `uv tool install` によるシステムインストール

`uv tool install` を使うと、プロジェクトディレクトリの外から `booklog-sync` コマンドを直接実行できるようになります。

```sh
uv tool install git+https://github.com/akihisa1210/booklog-to-obsidian.git
```

インストール後は以下のように実行できます。
```sh
booklog-sync sync --config /path/to/config.yaml
booklog-sync watch --config /path/to/config.yaml
```

更新する場合:
```sh
uv tool upgrade booklog-to-obsidian
```

### Windows タスクスケジューラでの自動起動

ログオン時に自動でファイル監視を開始するには、タスクスケジューラに登録します。

1. `Win + S` で「タスク スケジューラ」を検索して開きます。
2. 右側の操作パネルから「基本タスクの作成」をクリックします。
3. 名前を入力します（例: `BooklogSync`）。
4. トリガーで「ログオン時」を選択します。
5. 操作で「プログラムの開始」を選択し、以下を入力します。
   - **プログラム/スクリプト**: `booklog-sync.exe` のフルパス（例: `C:\Users\<ユーザー名>\.local\bin\booklog-sync.exe`）
   - **引数の追加**: `watch --config "C:\path\to\config.yaml"`
6. 「完了をクリックしたときに、このタスクのプロパティダイアログを開く」にチェックを入れて完了します。
7. プロパティの「全般」タブで「ユーザーがログオンしているかどうかにかかわらず実行する」を選択します。これによりターミナルウィンドウが表示されずバックグラウンドで実行されます。
8. プロパティの「設定」タブで「タスクを停止するまでの時間」のチェックを外します（デフォルトでは72時間で停止してしまうため）。

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

CSVのアイテムID（2列目）と`books_path`内のファイルの`item_id`の値が一致する場合、そのファイルのフロントマターをCSVの情報で更新します。

同期時にはフロントマターの差分を検出し、変更があったファイルのみを書き込みます。変更がないファイルはスキップされ、ファイルのタイムスタンプは更新されません。

### 制限事項

フロントマターの差分検出は、既存ファイルのYAML値とCSVから生成したデータの等価比較で行っています。本ツールが書き出したファイルをそのまま読み戻す場合は型が保持されますが、Obsidian等でフロントマターを手動編集し、数値風の文字列フィールド（`item_id`、`isbn13`、`publish_year`）からクォートを外すと、次回同期時にYAMLが数値として解釈され、差分ありと判定されて上書きが発生します。この場合、上書き後に本ツールが正しいクォート付きの値を書き戻すため、以降の同期では差分なしとして安定します。


## 開発者向け

### テスト実行
```sh
uv run pytest
```

### `python -m` での実行
```sh
uv run python -m booklog_sync sync
uv run python -m booklog_sync watch --config config.yaml
```
