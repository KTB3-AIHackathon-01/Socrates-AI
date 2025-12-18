from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
# import openai
from typing_extensions import TypedDict
from typing import Annotated
from operator import add
from dotenv import load_dotenv
import os, asyncio, sys
from pathlib import Path

# utils 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
# from utils.chat_history import save_chat_history, load_chat_history

load_dotenv()
# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = ChatOpenAI(
    model_name="gpt-5-nano",
    api_key=os.getenv("OPENAI_API_KEY_NANO"),
    base_url=os.getenv("OPENAI_BASE_URL_NANO")
)

class ChatState(TypedDict):
  # 초기 설정
  system_prompt: str
  topic: str
  brief_reaction: str
  next_question: str
  response_language: str
  checkpoints: list[str]

  # QnA 관련
  turn_count: int
  attempt_count: int
  prev_user_inputs: list[str]
  prev_ai_responses: list[str]
  user_input: str
  ai_response: str
  user_facing_message: str  # 표준화된 사용자 응답 메시지 필드

  # 상태 판정
  is_stuck: bool

  # 평가 및 Advanced 결과
  evaluation: dict
  advanced_response: dict
  next_action: str

# 함수
def load_system_prompt(topic: str) -> str:
  prompt_path = f"prompts/SYSTEM_PROMPT_INIT_EN.md"
  if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as f:
      template = f.read()
  
  prompt = template.replace("{topic}", topic)
  return prompt

def load_stuck_prompt(topic: str) -> str:
  prompt_path = f"prompts/SYSTEM_PROMPT_STUCK_EN.md"
  if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as f:
      template = f.read()
  
  prompt = template.replace("{topic}", topic)
  return prompt

def load_qna_prompt(topic: str) -> str:
  prompt_path = f"prompts/SYSTEM_PROMPT_QNA_EN.md"
  if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as f:
      template = f.read()
  
  prompt = template.replace("{topic}", topic)
  return prompt

def load_eval_prompt(topic: str) -> str:
  prompt_path = f"prompts/SYSTEM_PROMPT_EVAL_EN.md"
  if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as f:
      template = f.read()
  
  prompt = template.replace("{topic}", topic)
  return prompt


# 채팅 시작
def _chat_init(state: ChatState) -> ChatState:
  """시스템 프롬프트를 포함한 LLM 호출"""
  import json

  state["system_prompt"] = load_system_prompt(state["topic"])
  language_instruction = f"모든 응답을 {state['response_language']}로 해주세요." if state.get('response_language') else ""

  messages = [
    SystemMessage(content=state["system_prompt"]),
    SystemMessage(content=language_instruction)
  ]

  response = client.invoke(messages)
  response_text = response.content

  # JSON 형식으로 파싱
  try:
    response_data = json.loads(response_text)
    state["brief_reaction"] = response_data.get("brief_reaction", "")
    state["next_question"] = response_data.get("next_question", "")
    # 표준화: user_facing_message에서 실제 사용자 메시지 추출
    state["user_facing_message"] = response_data.get("user_facing_message", response_data.get("next_question", ""))
    state["checkpoints"] = response_data.get("checkpoints", [])
  except json.JSONDecodeError:
    # JSON 파싱 실패 시 전체 응답 저장
    state["next_question"] = response_text
    state["user_facing_message"] = response_text
    state["checkpoints"] = []

  return state

async def chat_init(topic: str) -> str:
  graph = StateGraph(ChatState)
  graph.add_node("chat_init", _chat_init)

  graph.add_edge(START, "chat_init")
  graph.add_edge("chat_init", END)

  app = graph.compile()
  result = app.invoke({
    "system_prompt": "",
    "topic": topic,
    "brief_reaction": "",
    "next_question": "",
    "user_facing_message": "",
    "response_language": "Korean",
    "checkpoints": [],
    "turn_count": 0,
    "attempt_count": 0,
    "prev_user_inputs": [],
    "prev_ai_responses": [],
    "user_input": "",
    "ai_response": "",
    "is_stuck": False,
    "evaluation": {},
    "advanced_response": {},
    "next_action": "",
  })

  # 채팅 결과를 JSON 파일로 저장
  # json_file = save_chat_history(result)
  # print(f"채팅 기록 저장: {json_file}")
  return result

# 채팅 중간
# 막힘 감지
def _detect_stuck(state: ChatState) -> ChatState:
  """사용자 답변에서 막힘 여부 판단"""
  import json

  stuck_prompt = load_stuck_prompt(state["topic"])
  language_instruction = f"모든 응답을 {state['response_language']}로 해주세요." if state.get('response_language') else ""

  messages = [
    SystemMessage(content=stuck_prompt),
    SystemMessage(content=language_instruction),
    HumanMessage(content=state["user_input"])
  ]

  response = client.invoke(messages)
  response_text = response.content

  try:
    response_data = json.loads(response_text)
    state["is_stuck"] = response_data.get("is_stuck", False)

    # 표준화: user_facing_message에서 실제 사용자 메시지 추출
    hint_msg = response_data.get("user_facing_message", response_data.get("ai_response", "생각해볼까요?"))

    # 막혔을 때 카운트 증가 및 메시지 생성
    if state["is_stuck"]:
      state["attempt_count"] += 1
      remaining = 3 - state["attempt_count"]  # 최대 3회 기회

      # 남은 기회 정보 추가
      if remaining > 0:
        state["user_facing_message"] = f"{hint_msg}\n(남은 기회: {remaining}회)"
        state["ai_response"] = state["user_facing_message"]
      else:
        state["user_facing_message"] = f"{hint_msg}\n(마지막 기회입니다)"
        state["ai_response"] = state["user_facing_message"]
    else:
      # 정상 답변이면 attempt_count 리셋
      state["attempt_count"] = 0
      state["user_facing_message"] = hint_msg
      state["ai_response"] = hint_msg

  except json.JSONDecodeError:
    state["is_stuck"] = False
    state["attempt_count"] = 0
    state["user_facing_message"] = response_text
    state["ai_response"] = response_text

  return state

# 채팅 내용으로 평가
def _chat_eval(state: ChatState) -> ChatState:
  """전체 대화 기록을 기반으로 학습 진행도 평가"""
  import json

  state["system_prompt"] = load_eval_prompt(state["topic"])
  language_instruction = f"모든 응답을 {state['response_language']}로 해주세요." if state.get('response_language') else ""

  # 평가용 입력 데이터 구성 (전체 대화 기록)
  eval_data = {
    "topic": state["topic"],
    "checkpoints": state.get("checkpoints", []),
    "user_inputs": state.get("prev_user_inputs", []),
    "ai_responses": state.get("prev_ai_responses", [])
  }

  messages = [
    SystemMessage(content=state["system_prompt"]),
    SystemMessage(content=language_instruction),
    HumanMessage(content=json.dumps(eval_data, ensure_ascii=False))
  ]

  response = client.invoke(messages)
  response_text = response.content

  # JSON 형식의 평가 결과 파싱
  try:
    evaluation_result = json.loads(response_text)
    state["evaluation"] = evaluation_result
  except json.JSONDecodeError:
    state["evaluation"] = {
      "error": "평가 결과 파싱 실패",
      "raw_response": response_text
    }

  return state

def load_advanced_prompt(topic: str) -> str:
  prompt_path = f"prompts/SYSTEM_PROMPT_ADVANCED_EN.md"
  if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as f:
      template = f.read()

  prompt = template.replace("{topic}", topic)
  return prompt

def _chat_advanced(state: ChatState) -> ChatState:
  """평가 결과를 기반으로 진행도에 맞는 질문 또는 리포트 생성"""
  import json

  advanced_prompt = load_advanced_prompt(state["topic"])
  language_instruction = f"모든 응답을 {state['response_language']}로 해주세요." if state.get('response_language') else ""

  # Advanced 프롬프트에 전달할 입력 데이터
  advanced_data = {
    "topic": state["topic"],
    "checkpoints": state.get("checkpoints", []),
    "prev_user_inputs": state.get("prev_user_inputs", []),
    "prev_ai_responses": state.get("prev_ai_responses", []),
    "attempt_count": state.get("attempt_count", 0),
    "turn_count": state.get("turn_count", 1),
    "evaluation": state.get("evaluation", {})
  }

  messages = [
    SystemMessage(content=advanced_prompt),
    SystemMessage(content=language_instruction),
    HumanMessage(content=json.dumps(advanced_data, ensure_ascii=False))
  ]

  response = client.invoke(messages)
  response_text = response.content

  # JSON 형식의 응답 파싱
  try:
    advanced_result = json.loads(response_text)

    # 응답 타입에 따라 처리
    response_type = advanced_result.get("response_type", "")

    if response_type == "progress_report":
      # 리포트인 경우 별도 필드에 저장
      state["advanced_response"] = advanced_result
      # 표준화: user_facing_message 추출
      state["user_facing_message"] = advanced_result.get("user_facing_message", "")
      state["ai_response"] = state["user_facing_message"]
      state["next_action"] = "end_session"
    else:
      # 질문인 경우 일반 응답으로 저장
      # 표준화: user_facing_message에서 실제 질문 추출
      question_msg = advanced_result.get("user_facing_message", advanced_result.get("question", response_text))
      state["user_facing_message"] = question_msg
      state["ai_response"] = question_msg
      state["advanced_response"] = advanced_result
      state["next_action"] = "continue"

  except json.JSONDecodeError:
    # JSON 파싱 실패 시 원본 응답 사용
    state["ai_response"] = response_text
    state["user_facing_message"] = response_text
    state["advanced_response"] = {
      "error": "응답 파싱 실패",
      "raw_response": response_text
    }
    state["next_action"] = "continue"

  return state

def route_after_detect(state: ChatState) -> str:
  """막힘 여부에 따라 다음 노드 결정"""
  if state["is_stuck"]:
    return "stuck"  # 막혔으면 stuck 노드로
  else:
    return "eval"  # 정상이면 advanced 노드로

async def chat_qna(session_id: str, user_input: str, topic: str) -> str:
  """
  기존 세션에 새로운 대답을 추가하는 함수
  Flow: detect_stuck → (stuck/eval) → advanced

  Args:
    session_id: 저장된 세션 ID
    user_input: 사용자 입력
    topic: 토픽
  """
  graph = StateGraph(ChatState)
  graph.add_node("detect_stuck", _detect_stuck)
  graph.add_node("eval", _chat_eval)
  graph.add_node("advanced", _chat_advanced)

  graph.add_edge(START, "detect_stuck")
  graph.add_conditional_edges(
    "detect_stuck",
    route_after_detect,
    {"eval": "eval", "stuck": END}
  )
  graph.add_edge("eval", "advanced")
  graph.add_edge("advanced", END)

  app = graph.compile()

  # 기존 대화 기록 로드
  # chat_history = load_chat_history(session_id)

  result = app.invoke({
    "system_prompt": "",
    "topic": topic,
    "brief_reaction": "",
    "next_question": "",
    "user_facing_message": "",
    # "turn_count": len(chat_history["conversation"]) + 1,
    # "attempt_count": chat_history.get("attempt_count", 0),
    # "prev_user_inputs": [c["user_input"] for c in chat_history["conversation"]],
    # "prev_ai_responses": [c["ai_response"] for c in chat_history["conversation"]],
    # "checkpoints": chat_history.get("checkpoints", []),
    "turn_count": 0,
    "attempt_count": 0,
    "prev_user_inputs": [],
    "prev_ai_responses": [],
    "checkpoints": [],
    "user_input": user_input,
    "ai_response": "",
    "response_language": "Korean",
    "is_stuck": False,
    "evaluation": {},
    "advanced_response": {},
    "next_action": "",
  })

  # # 대화 내용 업데이트
  # from utils.chat_history import append_to_conversation
  # append_to_conversation(session_id, user_input, result["ai_response"])

  return result

# # 디버그 메인테스트
# if __name__ == "__main__":
#   import sys
#   import time
#   topic = sys.argv[1]
#   user_input = sys.argv[2]
  
#   start_time = time.time()

#   # result = asyncio.run(chat_init(topic))
#   result = asyncio.run(chat_qna("945750df-6fc5-480c-a165-fd1817318249", user_input, topic))

#   print(result)
#   print("---------"*50)
#   print("brief_reaction:", result["brief_reaction"])
#   print("next_question:", result["next_question"])

#   end_time = time.time()
#   print(f"processing time : {end_time - start_time:.2f}s")

