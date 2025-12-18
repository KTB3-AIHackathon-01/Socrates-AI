# from langgraph.graph import StateGraph, START, END
# from langchain_core.messages import SystemMessage, HumanMessage
# from langchain_openai import ChatOpenAI
# from langchain_ollama import ChatOllama
from ollama import Client
# import openai
from typing_extensions import TypedDict
from typing import Annotated
from operator import add
from dotenv import load_dotenv
import os, asyncio, sys
from pathlib import Path
import json

# utils 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.chat_history import save_chat_history, load_chat_history

load_dotenv()

client = Client(
  host="https://ollama.com",
  headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)

# 함수
def load_report_prompt() -> str:
  prompt_path = f"prompts/REPORT_PROMPT_EN.md"
  if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as f:
      prompt = f.read()
  
  return prompt

# 샘플 데이터
def load_sample_data() -> str:
  json_path = f"dummy_data/session_10turn_CNN_339f9f98.json"
  json_data = ""
  if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
      json_data = f.read()
  else:
    # Fallback: try to find any 10-turn session file
    import glob
    files = glob.glob("dummy_data/session_10turn_*.json")
    if files:
      with open(files[0], 'r', encoding='utf-8') as f:
        json_data = f.read()

  return json_data

async def make_report(session_id: str) -> str:
  report_prompt = load_report_prompt()
  # json_data = load_chat_history(session_id)
  # json_str = json.dumps(json_data)
  json_str = load_sample_data()

  messages = [
    {'role': 'system', 'content': report_prompt + "\n모든 응답은 한글로 해주세요"},
    {'role': 'user', 'content': json_str},
  ]

  print(messages)
  print("---" * 50)
  response = ""
  for part in client.chat('gpt-oss:120b-cloud', messages=messages, think="high", stream=False):
    if "message" in part:
      response = part[1]["content"]
  try:
    return response
  except json.JSONDecodeError:
    print("error in json")
    return

# 디버그
if __name__ == "__main__":
  import sys
  session_id = sys.argv[1]
  
  result: str = asyncio.run(make_report(session_id))
  print(result)