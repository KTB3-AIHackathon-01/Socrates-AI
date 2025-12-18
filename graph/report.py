from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os, asyncio, sys
from pathlib import Path
import json

# utils 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.chat_history import save_chat_history, load_chat_history

load_dotenv()

client = OpenAI()

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
  try:
    response = client.responses.create(model="openai.gpt-oss-120b", input=messages)
    print(response)
    print("---" * 50)
    # return response.content[0].text
    return ""
  except json.JSONDecodeError:
    print("error in json")
    return

# ------------ #
# 하루 리포트 생성
def load_daily_prompt() -> str:
  prompt_path = f"prompts/ANALYSIS_DAY_PROMPT_EN.md"
  if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as f:
      prompt = f.read()
  
  return prompt

# 샘플 데이터 호출 (총 3개)
# 실제 DB에서는 현재 날짜와 세션 생성 날짜를 비교해서 데이터를 가져와야 함
# 시간은 오후 6시 기준
def load_sample_data_for_daily() -> str:
  json_path_1 = f"dummy_data/session_2turn_React Hooks_dd335390.json"
  json_path_2 = f"dummy_data/session_5turn_CNN_c9d3d6c5.json"
  json_path_3 = f"dummy_data/session_10turn_Git Basics_c574811e.json"

  json_paths = [json_path_1, json_path_2, json_path_3]
  json_data = []

  for json_path in json_paths:
    if os.path.exists(json_path):
      with open(json_path, 'r', encoding='utf-8') as f:
        json_data.append(f.read())

  return json_data

# 1일 분석 데이터 생성
async def make_daily_report(session_ids: List[str]) -> str:
  user_daily_prompt = load_daily_prompt()
  # 더미 데이터
  json_data = load_sample_data_for_daily()
  

# 디버그
if __name__ == "__main__":
  import sys
  session_id = sys.argv[1]
  
  # result: str = asyncio.run(make_report(session_id))
  # print(result)

  result: str = asyncio.run(make_daily_report([]))
  print(result)