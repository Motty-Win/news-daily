import feedparser, time
from typing import List, Dict


def fetch_feed(url: str) -> List[Dict[str, str]]:
    try:
        print(f"[DEBUG] Fetching feed from URL: {url}")
        d = feedparser.parse(url)
        # Check for feed parsing errors
        if d.bozo:
            print(f"[ERROR] Feed parsing error: {d.bozo_exception}")
            raise ValueError(
                f"フィードの解析中にエラーが発生しました: {d.bozo_exception}"
            )
        print("[DEBUG] Feed parsed successfully.")

        items = []
        titles_seen = set()

        for e in d.entries:
            title = getattr(e, "title", "")
            if title in titles_seen:
                continue  # 重複タイトルをスキップ
            titles_seen.add(title)

            items.append(
                {
                    "title": title,
                    "link": getattr(e, "link", ""),
                    "summary": getattr(e, "summary", ""),
                    "published": getattr(e, "published", ""),
                    "published_ts": (
                        time.mktime(getattr(e, "published_parsed", time.gmtime(0)))
                        if getattr(e, "published_parsed", None)
                        else 0
                    ),
                    "source": d.feed.get("title", url),
                }
            )

        return items
    except Exception as e:
        print(f"[ERROR] An error occurred while fetching the feed: {e}")
        return []
