# LangGraph 学習: 多機能タスク秘書エージェント

## Context（なぜ作るか）

LangGraph を「一通り触って理解する」ことが目的。題材は **対話 × 業務自動化**、LLM は **ローカル（Ollama, 導入済み）**。
グリーンフィールド（`test-langgraph` は依存ゼロ・`src/` のみの空プロジェクト）なので、LangGraph の主要機能を段階的に積み上げる構成で「多機能タスク秘書」を作る。

タスク秘書を選ぶ理由: 1リクエスト＝1判断が小さく区切れるため小型ローカルLLMでも回しやすく、かつ **ルーティング / ツール呼び出し / 状態蓄積 / メモリ・永続化 / human-in-the-loop / サブグラフ** という LangGraph のコア機能をひと通り自然に盛り込める。

### 環境（確認済み）
- Ollama 導入済み。モデル: `gemma4:12b`（汎用・高性能）, `Qwen2.5-Coder`（tool calling 実績あり）。両方とも tool calling 対応。
- `uv 0.9.5` / Python（プロジェクトは `requires-python >=3.13`）。

## 機能スコープ（タスク秘書としてできること）
- タスク登録 / 一覧表示 / 完了・削除 / 期限設定
- 期限が近い・過ぎたタスクのリマインド抽出
- 溜まったタスク・完了履歴の「日報要約」生成
- 自然言語の入力を intent 分類してそれぞれの機能へルーティング

## アーキテクチャ（StateGraph を手書きして学ぶ）

学習目的なので `create_react_agent` の一発ではなく、低レベル `StateGraph` を自分で組む。

```
src/task_secretary/
  __init__.py
  config.py      # モデル名など設定（OLLAMA_MODEL の切替）
  llm.py         # ChatOllama 生成（langchain-ollama）
  state.py       # State 定義（TypedDict + messages, add_messages reducer）
  tools.py       # タスクCRUDツール群（@tool, SQLite 永続化）
  db.py          # SQLite 初期化・接続（tasks テーブル）
  graph.py       # StateGraph 構築（ルーティング/ToolNode/interrupt/checkpointer）
  main.py        # CLI 対話ループ（thread_id 指定）
data/tasks.db    # タスク永続化（.gitignore 済みディレクトリ）
```

### グラフ構成
- **State**: `messages`（`add_messages` reducer）＋必要なら `intent` フィールド。
- **classify ノード**: 入力 intent を「task_ops / report / chat」に分類 → **conditional edge** で分岐。
- **agent ノード**: `llm.bind_tools(tools)` でツール呼び出しを判断。
- **ToolNode**: `tools.py` の CRUD ツールを実行 → agent に戻る **ツール実行ループ**。
- **report サブグラフ**: 完了/未完タスクを集計して要約を生成（サブグラフ化して合成を学ぶ）。
- **human-in-the-loop**: 削除など破壊的操作の前に `interrupt()` で確認 → 承認後に実行。
- **checkpointer**: まず `MemorySaver`、次に `SqliteSaver` に差し替えて `thread_id` 単位の会話メモリ・永続化を学ぶ。

## 段階的な実装ステップ（各ステップで動かして学ぶ）

1. **セットアップ**: `uv add langgraph langchain-ollama langchain-core langgraph-checkpoint-sqlite`。`llm.py` で `ChatOllama` 疎通確認（単発 invoke）。
2. **最小グラフ**: 1ノードだけの対話ループ（`StateGraph` + `add_messages`）を CLI で動かす。
3. **ツール導入**: `tools.py` にタスク CRUD（SQLite）を `@tool` で定義 → `bind_tools` + `ToolNode` でツール実行ループ。「タスク追加して」「一覧見せて」が通ることを確認。
4. **ルーティング**: classify ノード + conditional edge で task_ops / report / chat を振り分け。
5. **メモリ・永続化**: checkpointer を `MemorySaver`→`SqliteSaver` に。再起動しても `thread_id` で会話継続。
6. **human-in-the-loop**: 削除前に `interrupt()` で承認フロー。
7. **サブグラフ**: 日報要約をサブグラフ化して親グラフに合成。
8. **（任意）可視化**: `langgraph-cli[inmem]` を入れて `langgraph dev` で LangGraph Studio からグラフを可視化。

## 再利用・既存の利用
- 既存コードはほぼ無いため新規実装。LangGraph 標準の `add_messages` reducer / `ToolNode` / `MemorySaver` / `SqliteSaver` / `interrupt` をそのまま活用し、車輪の再発明を避ける。
- LLM 接続は `langchain-ollama` の `ChatOllama` を使用（Ollama 公式連携）。

## ローカルLLM特有の注意（プランに織り込む）
- tool calling の安定度はモデル依存。まず **Qwen2.5-Coder** で tool 呼び出しを確認し、汎用対話・要約は **gemma4:12b** を試す。`config.py` でモデル切替可能にする。
- 小型モデルは多段推論が弱いので、classify を独立ノードにして1回1判断に分解（上の設計はこれに沿っている）。
- tool calling がどうしても不安定な場合のフォールバック: structured output（`with_structured_output`）かプロンプトベースの JSON 抽出に切替。

## 検証（エンドツーエンド）
- `uv run python -m task_secretary.main` で CLI 起動し、次を順に確認:
  1. 「明日までにレポート提出のタスク追加して」→ SQLite に行が入る。
  2. 「タスク一覧」→ 登録分が返る。
  3. 「3番のタスク削除して」→ `interrupt` で確認プロンプト → 承認で削除。
  4. 「今日の日報まとめて」→ report サブグラフが要約を返す。
  5. CLI を再起動し同じ `thread_id` で続き → 会話・タスクが永続化されている。
- `sqlite3 data/tasks.db "select * from tasks;"` で永続化を直接確認。
- （任意）`langgraph dev` で Studio を開きノード遷移を目視。

## 未確定・実装時に決める
- デフォルトモデル（gemma4:12b か Qwen2.5-Coder か）は Step 3 のツール呼び出し安定性を見て決定。
- 日報要約をサブグラフにするかマルチエージェント（別 agent ノード）にするかは Step 7 で比較。
