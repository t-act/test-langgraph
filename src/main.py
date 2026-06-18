"""CLI 対話ループ。Step 2 を動かすエントリポイント。

    uv run python src/main.py
"""
from graph import build_graph
import db


def main() -> None:
    graph = build_graph()
    db.init_db()
    print("タスク秘書（最小版）です。終了は exit / quit。")

    while True:
        user = input("you> ").strip()
        if user in {"exit", "quit", "q"}:
            break
        if not user:
            continue

        # TODO(step2):
        #   1. graph.invoke({"messages": [{"role": "user", "content": user}]}) を呼ぶ
        result = graph.invoke({"messages": [{"role": "user", "content": user}]})

        #   2. 戻り値 result の result["messages"][-1] が最新の応答(AIMessage)
        ai_message = result["messages"][-1]

        #   3. その .content を "bot> ..." の形で表示する
        print("bot> ", ai_message.content)


if __name__ == "__main__":
    main()
