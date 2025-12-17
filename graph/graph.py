from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import sys
import os
from datetime import datetime
from uuid import uuid4

# 상대 경로 import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.state import LearningState, Message
from config.config import OPENAI_API_KEY, MODEL_NAME, SYSTEM_PROMPT_PATH
import db.db as db

# LLM 초기화
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=MODEL_NAME, temperature=0.7)

def load_system_prompt(topic: str) -> str:
  """시스템 프롬프트 로드 및 주제 삽입"""
  try:
      with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
          template = f.read()
      return template.replace("{topic}", topic)
  except FileNotFoundError:
      return f"당신은 '{topic}'에 대해 소크라테스식으로 가르치는 선생님입니다."

def initialize_node(state: LearningState) -> LearningState:
  """대화 초기화 노드 - 시스템 프롬프트 로드"""
  system_prompt = load_system_prompt(state["topic"])
  
  state["system_prompt"] = system_prompt
  state["conversation_phase"] = "initial"
  state["progress"] = 0
  state["attempt_count"] = 0
  state["misconceptions"] = []
  state["difficulty_level"] = "basic"
  state["messages"] = []
  state["checkpoints"] = []
  state["should_save_checkpoint"] = False
  
  # DB에 세션 저장
  db.create_session(state["session_id"], state["topic"])
  
  return state

def generate_initial_question_node(state: LearningState) -> LearningState:
  """대화 초기 - 첫 질문 생성"""
  system_prompt = state["system_prompt"]
  
  messages = [
      SystemMessage(content=system_prompt),
      HumanMessage(content="학습을 시작해주세요.")
  ]
  
  response = llm.invoke(messages)
  question = response.content
  
  state["current_question"] = question
  state["messages"].append({
      "role": "assistant",
      "content": question,
      "timestamp": datetime.now()
  })
  
  db.save_message(state["session_id"], "assistant", question)
  
  return state

def process_user_response_node(state: LearningState) -> LearningState:
  """대화 중 - 사용자 응답 처리"""
  if not state["messages"]:
      return state
  
  # 마지막 사용자 메시지 가져오기
  user_response = state["messages"][-1]["content"]
  
  # 응답 분석
  system_prompt = state["system_prompt"]
  
  messages = [
      SystemMessage(content=system_prompt),
  ]
  
  # 대화 이력 추가
  for msg in state["messages"]:
      if msg["role"] == "user":
          messages.append(HumanMessage(content=msg["content"]))
      else:
          messages.append(SystemMessage(content=msg["content"]))
  
  response = llm.invoke(messages)
  next_question = response.content
  
  state["current_question"] = next_question
  state["messages"].append({
      "role": "assistant",
      "content": next_question,
      "timestamp": datetime.now()
  })
  
  # 진도도 업데이트 (간단한 방식: 메시지 수 기반)
  state["progress"] = min((len(state["messages"]) / 10) * 100, 100)
  state["attempt_count"] += 1
  state["should_save_checkpoint"] = True
  
  db.save_message(state["session_id"], "assistant", next_question)
  
  return state

def router_node(state: LearningState) -> str:
  """라우터 - 대화 단계 결정"""
  if state["conversation_phase"] == "initial":
      return "generate_initial_question"
  elif state["progress"] >= 100 or state["attempt_count"] >= 5:
      return "closing_phase"
  else:
      return "process_response"

def closing_phase_node(state: LearningState) -> LearningState:
  """대화 종료 - 최종 요약"""
  system_prompt = state["system_prompt"]
  
  summary_prompt = "지금까지의 대화를 요약하고 학습자의 이해도를 평가해주세요."
  
  messages = [
      SystemMessage(content=system_prompt),
      HumanMessage(content=summary_prompt)
  ]
  
  response = llm.invoke(messages)
  summary = response.content
  
  state["messages"].append({
      "role": "assistant",
      "content": summary,
      "timestamp": datetime.now()
  })
  
  state["conversation_phase"] = "closing"
  state["should_save_checkpoint"] = True
  
  db.save_message(state["session_id"], "assistant", summary)
  
  return state

def checkpoint_node(state: LearningState) -> LearningState:
  """체크포인트 저장 노드"""
  if state["should_save_checkpoint"]:
      db.save_checkpoint(
          session_id=state["session_id"],
          turn=state["attempt_count"],
          phase=state["conversation_phase"],
          progress=state["progress"],
          misconceptions=state["misconceptions"],
          attempt_count=state["attempt_count"]
      )
      state["should_save_checkpoint"] = False
  
  return state

# 그래프 구성
def create_graph():
  """LangGraph 그래프 생성"""
  graph = StateGraph(LearningState)
  
  # 노드 추가
  graph.add_node("initialize", initialize_node)
  graph.add_node("generate_initial_question", generate_initial_question_node)
  graph.add_node("process_response", process_user_response_node)
  graph.add_node("closing_phase", closing_phase_node)
  graph.add_node("checkpoint", checkpoint_node)
  
  # 엣지 추가
  graph.add_edge("initialize", "generate_initial_question")
  graph.add_edge("generate_initial_question", "checkpoint")
  graph.add_edge("process_response", "checkpoint")
  graph.add_edge("checkpoint", "router")
  
  # 조건부 라우팅
  graph.add_conditional_edges(
      "router",
      router_node,
      {
          "generate_initial_question": "generate_initial_question",
          "process_response": "process_response",
          "closing_phase": "closing_phase"
      }
  )
  
  graph.add_edge("closing_phase", END)
  
  # 진입점
  graph.set_entry_point("initialize")
  
  return graph.compile()

# 그래프 인스턴스
learning_graph = create_graph()

def run_learning_session(topic: str, user_input: str = None) -> dict:
    """학습 세션 실행"""
    session_id = str(uuid4())
    
    initial_state: LearningState = {
      "session_id": session_id,
      "topic": topic,
      "messages": [],
      "conversation_phase": "initial",
      "progress": 0,
      "attempt_count": 0,
      "misconceptions": [],
      "difficulty_level": "basic",
      "system_prompt": "",
      "current_question": None,
      "checkpoints": [],
      "should_save_checkpoint": False
    }
    
    # 그래프 실행
    result = learning_graph.invoke(initial_state)
    
    return {
      "session_id": result["session_id"],
      "current_question": result["current_question"],
      "progress": result["progress"],
      "phase": result["conversation_phase"]
    }