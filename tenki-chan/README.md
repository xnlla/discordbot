# tenki-chan

## 概要

今日の天気と明日の天気と、気分をポストするだけのbotです

## 使用方法

Docker 動作環境のある、24 時間稼働するコンピュータ上で実行してください。

### build & deploy

Discord developer hub よりアプリケーションを作成し、以下の権限を持ったアクセストークンを取得してください。

- `bot`
  - Send Messages

リポジトリをクローンします。

```sh
git clone
cd tenki-chan
```

`.env`ファイルを作成してください。`CHANNEL_ID`は、botがアクセス可能なチャンネル ID を指定してください。
また、botが使用するため、ユーザはこれに書き込みを行わないでください。

```env
TOKEN=XXXXXXXXXXXXXXX
CHANNEL_ID=YYYYYYYYYYYYYYY
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
