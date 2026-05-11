# kb-hook

Kanboard のイベントを Mattermost へ通知する Webhook サーバーです。

## 概要

Kanboard で発生したイベント（タスクの作成、およびカラムの移動）を Webhook で受け取り、指定された Mattermost のチャンネルへ通知を投稿します。
通知メッセージの生成には Jinja2 テンプレートを使用しており、カスタマイズが可能です。

## 機能

- Kanboard からの Webhook 受信
- Mattermost へのメッセージ投稿
- プロジェクトごとの通知先チャンネル切り替え
- 特定のカラム移動時のみの通知（フィルタリング）
- 通知メッセージのテンプレート化（Jinja2）

## セットアップ

### 必要条件

- Python 3.13
- uv
- go-task

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/sg-daigo/kb-hook.git
cd kb-hook

### 設定

`conf/config.ini` を編集して、Kanboard と Mattermost の接続情報を設定します。

```ini
[mattermost]
bot_token = <Your Mattermost Bot Token>
host = <Mattermost Host>
scheme = http
port = 8065

[kanboard]
url = <Your Kanboard URL>
token = <Kanboard Webhook Token>
api_token = <Kanboard API Token>

# プロジェクトごとの設定 (セクション名はプロジェクトID)
[1]
channel_id = <Mattermost Channel ID>
target_columns = 1, 2, 3, 4
```

- `kanboard.token`: Kanboard の Webhook 設定で指定するトークンです。
- `kanboard.api_token`: Kanboard の個人設定 > API より取得します。
- `target_columns`: 通知対象とするカラム ID をカンマ区切りで指定します。
- プロジェクトIDやカラムIDは、Kanboardの画面からは確認できないため、[ツール](https://github.com/sg-daigo/kb-tool.git)を用意しました。

## ビルド

```bash
task build
```

## 実行

```bash
task
task logs
```

## Kanboard 側の設定

1. Kanboard の「設定 > Webhook」を開きます。
2. Webhook URL に `http://<your-server>:3001/hook` を入力します。

## テンプレートのカスタマイズ

`templates/` ディレクトリ内の `.j2` ファイルを編集することで、通知メッセージの内容を変更できます。

- `task.create.j2`: タスク作成時のメッセージ
- `task.move.column.j2`: タスク移動時のメッセージ

### テンプレート変数
テンプレート内では以下の変数が利用できます：
- task: タスク情報（タイトル、説明など）
- project: プロジェクト情報
- column: カラム情報
- user: ユーザー情報

## ファイル構成

```
kb-hook/
├── app.py                 # メインアプリケーション
├── kb_event.py           # Kanboardイベント処理
├── mm_util.py            # Mattermost関連ユーティリティ
├── conf/                 # 設定ファイル
│   ├── config.ini        # メイン設定
│   └── logging.ini       # ログ設定
├── templates/            # メッセージテンプレート
├── docker/               # Docker関連ファイル
└── Taskfile.yml          # taskファイル
```

## トラブルシューティング
1. Webhook が動作しない
- トークンが正しく設定されているか確認
- Kanboard側のWebhook URLが正しいか確認
- サーバーのポートが開いているか確認
2. Mattermostに投稿されない
- Bot Tokenが有効か確認
- チャンネルIDが正しいか確認
- Botにチャンネルへの投稿権限があるか確認

## ライセンス
このプロジェクトは MIT ライセンスの下で公開されています。
