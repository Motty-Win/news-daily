import feedparser, time


# エラーハンドリングを追加
def fetch_feed(url: str):
    try:
        d = feedparser.parse(url)
        if d.bozo:
            raise ValueError(
                f"フィードの解析中にエラーが発生しました: {d.bozo_exception}"
            )
        items = []
        titles_seen = set()

        for e in d.entries:
            title = getattr(e, "title", "")
            if title in titles_seen:
                continue  # 重複タイトルをスキップ
            titles_seen.add(title)

            items.append(
                {
                    "title": title,  # 日本語訳せずそのまま表示
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
        return []
