"""設定値。学習の核ではないのでこちらで用意済み。

使うモデルは環境変数 OLLAMA_MODEL で切り替えられる:
    OLLAMA_MODEL=gemma4:12b uv run python src/main.py

手元にあるモデル:
    - Qwen2.5-Coder:latest  … tool calling 実績あり（後のステップ向き）
    - gemma4:12b            … 汎用・日本語対話が自然
"""
import os

# tool calling が正しく機能するのは gemma4:12b 側だったのでこちらを既定にする。
# （Qwen2.5-Coder:latest は tool_calls を返さずテキストで吐いてしまうため）
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:12b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
TEMPERATURE = 0.3
