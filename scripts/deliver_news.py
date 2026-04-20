"""今日の就職・採用・インターン関連ニュースをClaudeで生成してSlackに投稿する。"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic
import requests


MODEL_ID = "claude-sonnet-4-20250514"


def build_prompt() -> str:
    today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y年%-m月%-d日")
    return (
        f"今日の就職・採用・インターン関連の重要ニュースを3〜5件、"
        f"Slack投稿用に簡潔にまとめてください。"
        f"各ニュースは「・」で始め、ニュース名と1行の要約を記載してください。"
        f"冒頭に「📰 今日の就活ニュース（{today}）」をつけてください。"
    )


def generate_news(api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=1024,
        messages=[{"role": "user", "content": build_prompt()}],
    )
    parts = [block.text for block in response.content if block.type == "text"]
    return "".join(parts).strip()


def post_to_slack(webhook_url: str, text: str) -> None:
    response = requests.post(
        webhook_url,
        json={"text": text},
        timeout=30,
    )
    response.raise_for_status()


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    missing = [
        name
        for name, value in (
            ("ANTHROPIC_API_KEY", api_key),
            ("SLACK_WEBHOOK_URL", webhook_url),
        )
        if not value
    ]
    if missing:
        print(
            f"エラー: 環境変数が未設定です: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 1

    news_text = generate_news(api_key)
    if not news_text:
        print("エラー: ニュース本文が生成されませんでした。", file=sys.stderr)
        return 1

    post_to_slack(webhook_url, news_text)
    print("Slackへの投稿が完了しました。")
    print("---")
    print(news_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
