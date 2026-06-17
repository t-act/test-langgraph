"""グラフ構築。Step 3: タスクCRUDツールを LLM に持たせる。

   START --> chatbot --(ツール要求あり)--> tools --+
               ^                                     |
               +-------------------------------------+
               |
             (ツール要求なし) --> END

chatbot が「このツールを使って」と判断したら tools ノードで実行し、その結果を
持って chatbot に戻る。これがエージェントの基本ループ（いわゆる ReAct ループ）。
"""
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from llm import build_llm
from state import State
from tools import TOOLS

# Step3: bind_tools で「呼べるツール一覧」を LLM に教える。
#   これで LLM は応答に tool_calls（add_task をこの引数で、等）を含められる。
#   ※ chatbot 内ではこの tool 付き llm をそのまま invoke するだけでよい。
llm = build_llm().bind_tools(TOOLS)


def chatbot(state: State) -> dict:
    """会話履歴を LLM に渡し、応答（通常の返答 or ツール呼び出し要求）を返すノード。"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def build_graph():
    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot)
    # tools ノード: LLM が要求したツール呼び出しを実際に実行する（prebuilt）。
    builder.add_node("tools", ToolNode(TOOLS))

    builder.add_edge(START, "chatbot")

    # TODO(step3-a): chatbot の後を「条件分岐」にする。
    #   prebuilt の tools_condition は、直前の AI メッセージに tool_calls が
    #   あれば "tools" へ、無ければ END へ、を自動で振り分けてくれる。
    #     builder.add_conditional_edges("chatbot", tools_condition)
    #   ※ Step2 の add_edge("chatbot", END) は書かない。この分岐がその役割。

    # TODO(step3-b): tools の実行後は chatbot に戻してループさせる。
    #   ツール結果を見て LLM が最終返答を作れるようにするため。
    #     builder.add_edge("tools", "chatbot")

    return builder.compile()
