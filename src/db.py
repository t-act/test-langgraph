"""SQLite によるタスク永続化。ここは土台なので完成済み。

tasks テーブル:
    id         INTEGER PRIMARY KEY   -- タスク番号
    title      TEXT     NOT NULL     -- タスク内容
    due        TEXT                  -- 期限 'YYYY-MM-DD'（任意）
    done       INTEGER  NOT NULL     -- 0=未完了, 1=完了
    created_at TEXT     NOT NULL     -- 作成日時

tools.py からはここの関数を呼ぶだけにして、SQL の詳細はこのファイルに閉じ込める。
"""
import os
import sqlite3
from datetime import datetime

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.db")


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row  # 行を dict 風に扱える
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                due        TEXT,
                done       INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL
            )
            """
        )


def add_task(title: str, due: str | None = None) -> int:
    """タスクを1件追加し、採番された id を返す。"""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, due, done, created_at) VALUES (?, ?, 0, ?)",
            (title, due, datetime.now().isoformat(timespec="seconds")),
        )
        return cur.lastrowid


def list_tasks(include_done: bool = False) -> list[dict]:
    """タスク一覧を返す。include_done=False なら未完了のみ。"""
    sql = "SELECT * FROM tasks"
    if not include_done:
        sql += " WHERE done = 0"
    sql += " ORDER BY (due IS NULL), due, id"  # 期限が早い順、期限なしは後ろ
    with _connect() as conn:
        return [dict(row) for row in conn.execute(sql).fetchall()]


def complete_task(task_id: int) -> bool:
    """完了に更新。対象が存在すれば True。"""
    with _connect() as conn:
        cur = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        return cur.rowcount > 0


def delete_task(task_id: int) -> bool:
    """削除。対象が存在すれば True。"""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cur.rowcount > 0
