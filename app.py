import streamlit as st
import yaml, time
from utils.rss import fetch_feed
from utils.llm import summarize_item
from utils.nlp import cluster_by_title

# アプリ基本情報
st.set_page_config(page_title="Daily News Summarizer", layout="wide")
st.title("📰 一日ニュースまとめ")

# RSSフィード読み込み
# エラーハンドリングを追加
try:
    with open("feeds.yaml", "r") as f:
        feeds = yaml.safe_load(f)
except FileNotFoundError:
    st.error("feeds.yaml ファイルが見つかりません。")
    st.stop()
except yaml.YAMLError as e:
    st.error(f"feeds.yaml の解析中にエラーが発生しました: {e}")
    st.stop()

# サイドバー（設定）
with st.sidebar:
    st.header("設定")
    category_limits = {}
    for feed in feeds:
        category_limits[feed["name"]] = st.number_input(
            f"{feed['name']}の最大記事数", min_value=1, max_value=15, value=3, step=1
        )
    do_cluster = st.checkbox("類似記事をまとめる", value=True)
    threshold = 0.6  # デフォルト値を設定
    st.caption("※要約はAPIを使用します。")

    # スタートボタン
    start_button = st.button("ニュースを取得")

# ニュース取得処理をスタートボタンに連動
if start_button:
    rows = []
    for feed in feeds:
        items = fetch_feed(feed["url"])[: category_limits[feed["name"]]]
        for it in items:
            it["category"] = feed["name"]
        rows.extend(items)

    # 日付順で並べ替え（新しい順）
    rows = sorted(rows, key=lambda x: x["published_ts"], reverse=True)

    # フィードが空の場合
    if not rows:
        st.info("フィードが空でした。feeds.yamlを見直してください。")
        st.stop()

    # 類似記事まとめ（クラスタリング）
    clusters = (
        cluster_by_title(rows, n_clusters=None, distance_threshold=threshold)
        if do_cluster
        else [[i] for i in range(len(rows))]
    )

    md_out = ["# 今日のニュースまとめ\n"]

    # 各クラスタごとに要約
    for ci, cluster in enumerate(clusters, start=1):
        section_items = [rows[i] for i in cluster]
        head = section_items[0]["title"] if section_items else f"トピック {ci}"
        st.subheader(f"{ci}. {head}")

        merged_text = "\n\n".join(
            f"- {it['title']}（{it['source']}）\n{it['summary']}\n{it['link']}\n（カテゴリ: {it['category']}）"
            for it in section_items
        )

        with st.spinner("🧠 要約中..."):
            try:
                s = summarize_item(merged_text)  # 修正: summarize_itemに1つの引数を渡す
            except Exception as e:
                s = f"要約に失敗しました: {e}"

        st.markdown(f"{s}\n\n（カテゴリ: {section_items[0]['category']}）")
        md_out.append(s)
        with st.expander("🔎 関連記事一覧"):
            for it in section_items:
                st.markdown(
                    f"- **[{it['title']}]({it['link']})**  · {it['source']} · "
                    f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(it['published_ts']))} · カテゴリ: {it['category']}"
                )

    # Markdownとして出力保存
    md_all = "\n\n".join(md_out)
    st.download_button(
        "📥 Markdownとして保存", md_all, file_name="daily_news.md", mime="text/markdown"
    )
    st.success("✅ アプリの準備が完了しました！Streamlitを起動して確認しましょう🚀")
