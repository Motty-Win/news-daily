from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

SYSTEM = """あなたは敏腕ニュースエディターです。事実関係を崩さず簡潔に日本語で要約します。
- 重要ポイントを3つ以内で
- 数字・固有名詞を残す
- 断定しすぎず、誇張しない
"""


def summarize_item(text: str):
    try:
        if not text.strip():
            return "要約に失敗しました: 入力テキストが空です。"

        prompt = f"""
        次の記事を要約してください。
        - 箇条書きで最大3点

        本文:
        {text}"""
        print("[DEBUG] Prompt sent to LLM:", prompt)  # デバッグ用にプロンプトを出力

        res = llm.invoke([SystemMessage(content=SYSTEM), HumanMessage(content=prompt)])
        print("[DEBUG] Response from LLM:", res.content)  # デバッグ用に応答を出力

        return res.content
    except Exception as e:
        print("[ERROR] LLM invocation failed:", e)  # エラー詳細を出力
        return f"要約に失敗しました: {e}"
