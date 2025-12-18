from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os, asyncio, sys
from pathlib import Path
import json
from datetime import datetime, timedelta
import random

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

async def make_report(user_input: List[str]) -> str:
  report_prompt = load_report_prompt()
  user_str = "\n".join(user_input)

  messages = [
    {'role': 'system', 'content': report_prompt + "\n모든 응답은 한글로 해주세요"},
    {'role': 'user', 'content': user_str},
  ]

  try:
    response = client.responses.create(model="openai.gpt-oss-120b", input=messages)
    # print(response)
    # print("---" * 50)
    # 응답 구조: response.output[0].content[0].text
    if hasattr(response, 'output') and len(response.output) > 0:
      return response.output[0].content[0].text
    return ""
  except (AttributeError, IndexError, json.JSONDecodeError) as e:
    print(f"응답 파싱 에러: {e}")
    return ""

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
async def make_daily_report(session_chats: List[List[str]]) -> dict:
  """
  사용자의 모든 세션을 분석하여 종합 학습 프로필 생성

  Args:
    session_chats: 2차원 배열 - [[turn1, response1, turn2, response2, ...], [turn1, response1, ...]]
                   각 세션은 사용자 입력과 AI 응답이 교대로 나오는 배열

  Returns:
    dict: 종합 학습 분석 결과 (JSON)
  """
  user_daily_prompt = load_daily_prompt()

  # 입력 데이터를 JSON 형식으로 변환
  if isinstance(session_chats, list) and len(session_chats) > 0:
    # 2차원 배열을 세션 구조로 변환
    sessions = []

    for session_idx, session in enumerate(session_chats):
      if isinstance(session, list) and len(session) > 0:
        # 각 세션을 turn 구조로 변환 (user_input, ai_response 교대로)
        conversation = []
        for i in range(0, len(session) - 1, 2):
          if i + 1 < len(session):
            conversation.append({
              "turn": (i // 2) + 1,
              "user_input": session[i],
              "ai_response": session[i + 1]
            })

        if conversation:
          # session_date를 ISO 형식으로 생성 (2025-12-18 10:00 ~ 2025-12-19 04:00 범위)
          start_time = datetime(2025, 12, 18, 10, 0, 0)
          end_time = datetime(2025, 12, 19, 4, 0, 0)
          random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
          random_milliseconds = random.randint(0, 999)
          session_date_dt = start_time + timedelta(seconds=random_seconds, milliseconds=random_milliseconds)
          session_date_str = session_date_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random_milliseconds:03d}Z"

          sessions.append({
            "session_id": f"session_{session_idx}",
            "session_date": session_date_str,
            "topic": "Learning Session",
            "total_turns": len(conversation),
            "conversation": conversation,
            "checkpoints": []  # 체크포인트는 대화 내용에서 추론
          })

    if not sessions:
      return {"error": "No valid session data provided"}

    # JSON 배열 형식으로 변환
    json_input = json.dumps(sessions, ensure_ascii=False, indent=2)
    # print(f"입력 데이터:\n{json_input}\n")
  else:
    return {"error": "Invalid input format"}

  messages = [
    {'role': 'system', 'content': user_daily_prompt + "\n\n【중요】모든 응답은 JSON 형식이어야 합니다.\n- concept_mastery의 concept, evidence_question: 한글\n- learning_difficulty의 stuck_concepts: 한글\n- instructional_guidance (teaching_recommendations, next_session_goal, recommended_practice): 모두 한글로 작성하세요."},
    {'role': 'user', 'content': f"다음은 한 사용자의 모든 학습 세션 데이터입니다. 제공된 대화 내용에만 기반하여 종합 분석을 제공해주세요:\n\n{json_input}"},
  ]

  try:
    response = client.responses.create(model="openai.gpt-oss-120b", input=messages)
    # print("Daily Report Response:", response)
    # print("---" * 50)

    # 응답 구조: response.output[0].content[0].text
    if hasattr(response, 'output') and len(response.output) > 0:
      response_text = response.output[0].content[0].text
      # JSON 추출 시도
      try:
        # 마크다운 코드 블록 제거
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```"):
          cleaned_text = cleaned_text.split("```")[1]
          if cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:]
        cleaned_text = cleaned_text.strip()

        result = json.loads(cleaned_text)

        # 추가 필드 계산 및 추가
        # 1. 총 질문수: 전체 배열 개수 / 2
        total_questions = sum(len(session) for session in session_chats) // 2

        # 2. 이해도: concept_mastery의 understanding_score 평균
        concept_mastery = result.get("concept_mastery", [])
        if concept_mastery:
          understanding_scores = [c.get("understanding_score", 0) for c in concept_mastery]
          avg_understanding = sum(understanding_scores) / len(understanding_scores)
        else:
          avg_understanding = 0.0

        # 3. 최근 활동: 2025-12-18 10:00 ~ 2025-12-19 04:00 중 랜덤 시간
        start_time = datetime(2025, 12, 18, 10, 0, 0)
        end_time = datetime(2025, 12, 19, 4, 0, 0)
        random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
        random_milliseconds = random.randint(0, 999)
        recent_activity_dt = start_time + timedelta(seconds=random_seconds, milliseconds=random_milliseconds)
        recent_activity = recent_activity_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random_milliseconds:03d}Z"

        # 결과에 필드 추가
        result["total_questions"] = total_questions
        result["understanding_score"] = round(avg_understanding, 2)
        result["recent_activity"] = recent_activity

        # 4. 각 concept_mastery에 learning_activity_time 추가
        if concept_mastery:
          for concept in concept_mastery:
            random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
            random_milliseconds = random.randint(0, 999)
            learning_time_dt = start_time + timedelta(seconds=random_seconds, milliseconds=random_milliseconds)
            learning_time = learning_time_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random_milliseconds:03d}Z"
            concept["learning_activity_time"] = learning_time

        return result
      except json.JSONDecodeError:
        # JSON 파싱 실패 시 원본 텍스트 반환
        print(f"JSON 파싱 실패: {response_text}")
        return {"error": "JSON parsing failed", "raw_response": response_text}

    return {}
  except Exception as e:
    print(f"일일 리포트 생성 에러: {e}")
    return {"error": str(e)}

# 디버그
if __name__ == "__main__":
  import sys
  session_id = sys.argv[1]
  
  # result: str = asyncio.run(make_report(session_id))
  # print(result)

  result: str = asyncio.run(make_daily_report([]))
  print(result)