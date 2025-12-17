import os, sys, uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ws.manager import manager
from ws.handlers import handle_start_session, handle_user_response, handle_close_session
from ws.schemas import ClientMessage
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from uuid import uuid4
import json

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 환경변수 로드
load_dotenv()

app = FastAPI()
# CORS 설정 (외부 접근 허용)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
  """
  WebSocket 채팅 엔드포인트
  
  Usage:
  - 연결: ws://localhost:8000/ws/chat/{client_id}
  - 세션 시작: {"action": "start", "topic": "Python"}
  - 답변 제출: {"action": "respond", "session_id": "...", "answer": "..."}
  - 세션 종료: {"action": "close", "session_id": "..."}
  """
  session_id = None
  
  try:
    # 초기 연결 수락
    await websocket.accept()
    print(f"🔗 Client {client_id} connected")

    while True:
      # 클라이언트 메시지 수신
      data = await websocket.receive_text()
      message = ClientMessage(**json.loads(data))

      if message.action == "start":
        # 새 세션 시작
        session_id = str(uuid4())
        # 이 부분에서 세션 id를 DB에 저장
        await manager.connect(session_id, websocket)
        print(f"🎓 Starting session: {session_id}")
        await handle_start_session(session_id, message.topic)
          
      elif message.action == "respond":
        # 사용자 응답 처리
        if message.session_id:
          session_id = message.session_id
          await handle_user_response(session_id, message.answer)
        else:
          await manager.send_error("", "SESSION_ERROR", "Session ID required")
              
      elif message.action == "close":
        # 세션 종료
        if message.session_id:
          await handle_close_session(message.session_id)
        break
              
  except WebSocketDisconnect:
    print(f"Client {client_id} disconnected")
    if session_id:
      await manager.disconnect(session_id)
          
  except Exception as e:
    print(f"Error: {e}")
    if session_id:
      await manager.send_error(session_id, "INTERNAL_ERROR", str(e))

@app.get("/")
async def root():
  return JSONResponse(content={"success": True, "message": "Welcome to Socratic Learning API"})


if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)