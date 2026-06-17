"""Ollama 接続。ここも土台なので用意済み。

ChatOllama は LangChain のチャットモデル実装で、LangGraph のノードから
そのまま .invoke(messages) できる。messages には LangChain の
BaseMessage（HumanMessage 等）のリスト、または {"role", "content"} の
dict のリストを渡せる。
"""
from langchain_ollama import ChatOllama

import config


def build_llm() -> ChatOllama:
    return ChatOllama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=config.TEMPERATURE,
    )


if __name__ == "__main__":
    # 疎通確認: uv run python src/llm.py
    llm = build_llm()
    print(f"model = {config.OLLAMA_MODEL}")
    print(llm.invoke("一文で自己紹介して").content)
