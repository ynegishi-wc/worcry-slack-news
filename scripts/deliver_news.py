"""今日の就職・採用・インターン関連ニュースをClaudeで生成してSlackに投稿する。"""

import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import anthropic
import requests


MODEL_ID = "claude-sonnet-4-20250514"


def build_prompt() -> str:
    weekday_jp = ["月", "火", "水", "木", "金", "土", "日"]
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    today = f"{now.year}年{now.month}月{now.day}日({weekday_jp[now.weekday()]})"
    return (
        f"Web検索を使って、直近の平日（土日を除く直近3営業日）に配信された日本の就職・採用・長期インターン関連ニュースを\n"
        f"1件選び、以下のフォーマットで厳密に出力してください。\n"
        f"\n"
        f"---フォーマット---\n"
        f"就活ニュース｜{today}\n"
        f"*{{ニュースタイトル}}*\n"
        f"{{メディア名}}({{記事URL}})\n"
        f"—————————————\n"
        f"*ひとことSummary*\n"
        f"{{ニュースの内容を学生目線で2〜3行で要約}}\n"
        f"*読み解きPoint*\n"
        f"{{このニュースが就活生にとって何を意味するか。共感・気づきを促す視点で2〜3行}}\n"
        f"*おすすめAction*\n"
        f"{{このニュースを受けて就活生が今週できる具体的な行動を1〜2行}}\n"
        f"—————————————\n"
        f"{{締めの一言は、今日取り上げたニュースの内容に直接紐づいた就活アドバイスを1〜2文で書いてください。季節感・感情的な励ましは不要です。例：初任給の高い企業を取り上げた場合→「給与水準を比較するときは額面だけでなく、昇給率やストックオプションの有無も確認する習慣をつけましょう。」例：アルムナイ採用を取り上げた場合→「新卒での入社先は『ゴール』ではなく『起点』です。長期的なキャリアを意識して企業選びをしましょう。」}}\n"
        f"---ここまで---\n"
        f"\n"
        f"ルール：\n"
        f"- フォーマット外のテキストは一切出力しない\n"
        f"- 実在する記事のみ使用する。URLは実際に存在するもの"
    )


def generate_news(api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=2048,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": build_prompt()}],
    )
    parts = [block.text for block in response.content if block.type == "text"]
    text = "".join(parts).strip()
    marker = "就活ニュース｜"
    idx = text.find(marker)
    if idx != -1:
        text = text[idx:]
    return text.strip()


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

    if not news_text.startswith("就活ニュース｜"):
        print("投稿スキップ：フォーマット外の出力のため")
        print("---")
        print(news_text)
        return 0

    post_to_slack(webhook_url, news_text)
    print("Slackへの投稿が完了しました。")
    print("---")
    print(news_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
