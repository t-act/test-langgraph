"""グラフ全体で共有する State の定義。

LangGraph の State は「ノード間で受け渡す共有メモ」。各ノードは State の
一部を返し、その値が State にマージされる。どうマージするかを決めるのが
"reducer"。
会話履歴はノードが応答を返すたびに「追記」していきたいので、messages には
add_messages という reducer を使う（上書きではなく append される）。
"""
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class State(TypedDict):
    # TODO(step2): messages フィールドを定義する。
    #   - 会話メッセージのリストを保持する
    #   - reducer に add_messages を使い、ノードが返したメッセージを追記する
    #   - ヒント: Annotated[list, add_messages]
    messages: Annotated[list, add_messages]