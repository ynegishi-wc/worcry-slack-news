# Daily News Delivery

毎朝8時（日本時間）に、Claude APIで生成した「今日の就活ニュース」をSlackに自動投稿するGitHub Actionsワークフローです。

## 構成

- `scripts/deliver_news.py` — Claude (`claude-sonnet-4-20250514`) にニュースを生成させ、Slack Incoming Webhookに投稿するスクリプト
- `.github/workflows/news-delivery.yml` — 毎日 UTC 23:00（JST 08:00）に自動実行するワークフロー

外部ニュースAPIは使用せず、Claudeが生成したテキストをそのままSlackへ投稿します。

## セットアップ手順

### 1. リポジトリをGitHubへプッシュ

このディレクトリをGitリポジトリとして初期化し、GitHubへプッシュしてください。

```bash
cd news-delivery
git init
git add .
git commit -m "Initial commit"
git remote add origin git@github.com:<your-account>/<your-repo>.git
git push -u origin main
```

### 2. GitHub Secretsを登録

リポジトリの **Settings → Secrets and variables → Actions → New repository secret** から、以下の2つを登録してください。

| Secret名 | 内容 |
| --- | --- |
| `ANTHROPIC_API_KEY` | Anthropic Consoleで発行したAPIキー |
| `SLACK_WEBHOOK_URL` | 投稿先Slackチャンネルの Incoming Webhook URL |

> ⚠️ APIキーやWebhook URLはコードに直書きしないでください。必ずSecrets経由で渡します。

### 3. スケジュール

- UTC `0 23 * * *` = 日本時間 毎朝 8:00 に自動実行されます。
- GitHub Actionsのスケジュールは数分遅延することがあります（仕様）。

## 手動実行

### GitHub上から実行

**Actions タブ → Daily News Delivery → Run workflow** ボタンから即時実行できます（`workflow_dispatch` トリガー）。

### ローカルから実行

```bash
cd news-delivery
pip install anthropic requests
export ANTHROPIC_API_KEY="sk-ant-..."
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
python scripts/deliver_news.py
```

正常終了すると、Slackへの投稿完了メッセージと生成された本文が標準出力に表示されます。

## トラブルシューティング

- **Slackに投稿されない**: `SLACK_WEBHOOK_URL` が正しいか、Webhookが有効か確認してください。
- **APIエラー**: Anthropic Consoleでクレジット残高・APIキーの有効性を確認してください。
- **Actionsが動かない**: リポジトリがPrivateの場合、スケジュール実行が60日間無活動で停止することがあります。
