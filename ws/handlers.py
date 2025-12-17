from fastapi import WebSocket, WebSocketException
from ws.schemas import ClientMessage, ServerEvent
from ws.manager import manager
# from graph.graph import run_learning_session
import db.db as db
import asyncio
import json
from graph.graph import set_graph

async def handle_start_session(session_id: str, topic: str):
  """세션 시작 처리"""
  try:
    print(f"📚 [START_SESSION] Initializing session {session_id} for topic: {topic}")

    # 1. DB에 세션 저장
    db.create_session(session_id, topic)
    print(f"✅ [DB] Session created in database")

    # 2. 첫 번째 질문 생성
    # result = run_learning_session(topic)
    # question = result["current_question"]
    result = "hello"
    question = "question"

    # 3. 첫 질문을 DB에 저장 (assistant 역할)
    db.save_message(session_id, "assistant", question)
    print(f"✅ [DB] First question saved")

    # 4. 클라이언트에 전송
    question_event = {
      "event": "question",
      "session_id": session_id,
      "question": question,
      # "phase": result.get("phase", "initial"),
      # "progress": result.get("progress", 0)
    }

    await manager.broadcast_to_session(session_id, question_event)
    print(f"📨 [SENT] Question sent to client")

  except Exception as e:
    print(f"❌ [ERROR] {str(e)}")
    await manager.send_error(session_id, "SESSION_START_ERROR", str(e))

async def handle_user_response(session_id: str, answer: str):
  """사용자 응답 처리"""
  try:
    # 여기서 DB에 사용자 응답 저장
    # db.save_message(session_id, "user", answer)  ← 사용자 입력
    # 처리 중 알림
    processing_event = {
      "event": "processing",
      "session_id": session_id
    }
    await manager.broadcast_to_session(session_id, processing_event)
    
    # 응답 처리 (비동기)
    # TODO: DB에서 세션 상태 로드하여 계속 처리
    await asyncio.sleep(1)  # LLM 처리 시뮬레이션
    # next_question = "다음 질문입니다..."
    result = await set_graph(answer)
    print(result)
    next_question = result
    
    # 여기서 DB에 처리 결과 저장
    # db.save_message(session_id, "assistant", next_question)
    
    # 다음 질문 생성
    next_question_event = {
      "event": "question",
      "session_id": session_id,
      "question": next_question,
      "phase": "ongoing",
      "progress": 30
    }
    
    await manager.broadcast_to_session(session_id, next_question_event)
  except Exception as e:
    await manager.send_error(session_id, "RESPONSE_ERROR", str(e))

async def handle_close_session(session_id: str):
  """세션 종료 처리"""
  try:
    session_end_event = {
        "event": "session_end",
        "session_id": session_id,
        "summary": "학습이 완료되었습니다.",
        "final_report": {
            "total_progress": 100,
            "misconceptions": [],
            "recommendations": []
        }
    }
    
    await manager.broadcast_to_session(session_id, session_end_event)
    await manager.disconnect(session_id)
  except Exception as e:
    await manager.send_error(session_id, "CLOSE_ERROR", str(e))
