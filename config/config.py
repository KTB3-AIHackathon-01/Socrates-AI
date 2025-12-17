import os
from dotenv import load_dotenv

load_dotenv()

# LLM 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-nano")

# # 데이터베이스 설정
# DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/sqlite.db")
# os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# 학습 시스템 설정
SYSTEM_PROMPT_PATH = "./prompts/SYSTEM_PROMPT.md"
REPORT_PROMPT_PATH = "./prompts/REPORT_PROMPT.md"