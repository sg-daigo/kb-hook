# kb-hook

Kanboard のイベントを Mattermost へ通知する Webhook サーバーです。

## 概要

Kanboard で発生したイベント（タスクの作成、およびカラムの移動）を Webhook で受け取り、指定された Mattermost のチャンネルへ通知を投稿します。
通知メッセージの生成には Jinja2 テンプレートを使用しており、カスタマイズが可能です。また、タスクのタグに基づいた **ユーザーメンション機能** を備えています。

## 機能

* **Kanboard からの Webhook 受信**: タスク作成、カラム移動に対応。
* **Mattermost へのメッセージ投稿**: Botアカウント経由で投稿。
* **スレッド返信対応**: Kanboardタスクの「参照」欄にMattermostの投稿URLがある場合、自動的にその投稿のスレッドへ返信。
* **プロジェクトごとの通知先設定**: プロジェクトID単位で通知チャンネルを切り替え可能。
* **フィルタリング**: 特定のカラム移動時のみ通知するよう設定可能。
* **メンション機能**: タスクに紐付いたタグに基づき、Mattermost上のユーザーへメンションを飛ばす。
* **テンプレート化**: Jinja2 テンプレートにより通知内容を柔軟にカスタマイズ。

## セットアップ

### 必要条件

* Python 3.13
* uv
* go-task

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/sg-daigo/kb-hook.git
cd kb-hook

```

### 設定

#### 1. 接続設定 (`conf/config.ini`)

`conf/config.ini` を作成し、接続情報を設定します。

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

* `kanboard.token`: Kanboard の Webhook 設定で指定するトークンです。URLパラメータ `?token=xxx` と比較されます。
* `target_columns`: 通知対象とする移動先のカラム ID をカンマ区切りで指定します。
* プロジェクトIDやカラムID、タグIDの確認には [kb-tool](https://github.com/sg-daigo/kb-tool.git) が利用可能です。

#### 2. メンション設定 (`conf/mention.yml`)

タスクのタグIDと、Mattermostのユーザー名を紐付けます。

```yaml
# タグID: Mattermostユーザー名 (先頭の@は不要)
1: jsmith
2: team-dev

```

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

* `task.create.j2`: タスク作成時のメッセージ
* `task.move.column.j2`: カラム移動時のメッセージ

### 利用可能な変数 (`data` オブジェクト)

テンプレート内で `data.key` 形式でアクセス可能です。

| 変数名 | 内容 |
| --- | --- |
| `title` | タスクのタイトル |
| `url` | Kanboardタスクへの直リンク |
| `assignee_name` | 担当者名 |
| `category_name` | カテゴリ名 |
| `swimlane_name` | スイムレーン名 |
| `column_title` / `dst_column_title` | カラム名 / 移動先カラム名 |
| `src_column_title` | 移動元カラム名 (移動イベントのみ) |
| `creator_name` | 作成者名 (作成イベントのみ) |
| `user_name` | イベント実行ユーザー名 (移動イベントのみ) |

## ファイル構成

```
kb-hook/
├── app.py                # Flask Webサーバー・メインロジック
├── kb_event.py           # Kanboard API連携・メッセージ生成・メンション処理
├── mm_util.py            # Mattermost APIクライアント (mattermostdriver)
├── conf/                 # 設定ファイル格納ディレクトリ
│   ├── config.ini        # 接続・通知設定
│   ├── logging.ini       # ログ出力設定
│   └── mention.yml       # タグIDとユーザーの紐付け
├── templates/            # Jinja2 メッセージテンプレート
├── docker/               # Docker環境用ファイル (Image v1.1.0)
└── Taskfile.yml          # go-task 定義ファイル

```

## トラブルシューティング

1. **Webhook が動作しない**
* ログ (`logger.debug`) を確認し、`token不一致` が出ていないか確認してください。


2. **メンションが飛ばない**
* `mention.yml` のキーが「タグ名」ではなく「タグID（整数）」になっているか確認してください。



## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 変更履歴

### v1.1.0

* メンション機能を追加

### v1.0.0

* 初版リリース