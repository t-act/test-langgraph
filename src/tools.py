"""LLM が呼び出すツール群。@tool デコレータで普通の関数をツール化する。

【最重要ポイント】
  - 関数の docstring と引数の型注釈が、そのまま「LLM 向けのツール説明書」になる。
    LLM はこの説明を読んで「どのツールを・どんな引数で呼ぶか」を決める。
    なので docstring は LLM が誤解しないように具体的に書く。
  - ツール関数の戻り値（文字列）は、実行結果として LLM に返される。
    LLM はそれを読んで最終的な返答を作る。
  - 中身は db.py の関数を呼ぶだけ。永続化の詳細は db.py に任せる。
"""
from langchain_core.tools import tool
import db


@tool
def add_task(title: str, due: str | None = None) -> str:
    """新しいタスクを追加する。

    Args:
        title: タスクの内容（例: 'レポート提出'）。
        due: 期限。'YYYY-MM-DD' 形式の文字列。期限が無ければ省略する。
    """
    # TODO(step3): db.add_task(title, due) で追加し、採番された id を使って
    #   「タスクを追加しました（id=...）」のような結果文字列を return する。
    id = db.add_task(title, due)
    return f"タスクを追加しました（id={id}）"


@tool
def list_tasks() -> str:
    """未完了タスクの一覧を返す。"""
    # TODO(step3): db.list_tasks() を呼び、各タスクを
    #   「{id}: {title}（期限: {due}）」のような読みやすい1行に整形し、
    #   改行でつないで返す。1件も無ければ「タスクはありません」と返す。
    tasks = db.list_tasks()
    task_message = ""
    for task in tasks:
        task_message += f"{task["id"]}: {task["title"]}（期限: {task["due"]}）\n"
    return task_message


@tool
def complete_task(task_id: int) -> str:
    """指定した id のタスクを完了にする。"""
    # TODO(step3): db.complete_task(task_id) の戻り値(True/False)を見て、
    #   成功なら完了メッセージ、False なら「見つかりません」を返す。
    if db.complete_task(task_id):
        return "完了"
    else:
        return "見つかりません"


@tool
def delete_task(task_id: int) -> str:
    """指定した id のタスクを削除する。"""
    # TODO(step3): db.delete_task(task_id) の戻り値を見て成功/失敗を返す。
    if db.delete_task(task_id):
        return "完了"
    else:
        return "見つかりません"



# LLM に渡すツールのリスト（graph.py で bind_tools / ToolNode に渡す）
TOOLS = [add_task, list_tasks, complete_task, delete_task]
