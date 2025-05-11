# kaikei-san

## 概要

- 会計さんは、Discord チャンネルで単純な貸し/借りの帳簿を作成・差し引き会計を行える bot です。
- 本 bot は現在各サーバで稼働指せる前提であり、サービスとして設計されていません。

## 使用方法

Docker 動作環境のある、24 時間稼働するコンピュータ上で実行してください。

### build & deploy

Discord developer hub よりアプリケーションを作成し、以下の権限を持ったアクセストークンを取得してください。

- `applications.commands`
- `bot`
  - Read Message History（帳簿の読み込みに必須）
  - Send Messages（帳簿の書き込みに必須）

リポジトリをクローンします。

```sh
git clone
cd kaikei-san
```

`kaikeisan`ディレクトリへ`.env`ファイルを作成してください。`CHOUBO_ID`は、会計さんがアクセス可能なチャンネル ID を指定してください。
また、会計さんが使用するため、ユーザはこれに書き込みを行わないでください。

```env
TOKEN=XXXXXXXXXXXXXXX
CHOUBO_ID=YYYYYYYYYYYYYYY
```

コンテナを起動します。

```sh
docker-compose up -d
```

### ログの閲覧

以下のコマンドを実行します。
```sh
docker-compose logs
```

### destroy

コンテナを停止・破棄します。

```sh
docker-compose down --rmi all
```
