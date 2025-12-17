from typing import Dict, Set
from fastapi import WebSocket
import json

class ConnectionManager:
  def __init__(self):
    # session_id -> WebSocket 매핑
    self.active_connections: Dict[str, WebSocket] = {}
    # 세션별 대기 중인 연결들
    self.waiting_connections: Dict[str, Set[WebSocket]] = {}

  async def connect(self, session_id: str, websocket: WebSocket):
    """WebSocket을 연결 목록에 추가 (accept는 이미 완료되었다고 가정)"""
    self.active_connections[session_id] = websocket
    print(f"✅ Session {session_id} connected. Total: {len(self.active_connections)}")

  async def disconnect(self, session_id: str):
    if session_id in self.active_connections:
      del self.active_connections[session_id]

  async def broadcast_to_session(self, session_id: str, message: dict):
    """특정 세션에 메시지 브로드캐스트"""
    if session_id in self.active_connections:
      websocket = self.active_connections[session_id]
      try:
        await websocket.send_json(message)
        print(f"📨 Message sent to {session_id}: {message.get('event', 'unknown')}")
      except Exception as e:
        print(f"❌ Error sending message: {e}")
        await self.disconnect(session_id)
    else:
      print(f"⚠️  Session {session_id} not found in active connections")

  async def send_error(self, session_id: str, error_code: str, message: str):
    """에러 메시지 전송"""
    error_event = {
        "event": "error",
        "session_id": session_id,
        "error_code": error_code,
        "error_message": message
    }
    await self.broadcast_to_session(session_id, error_event)

manager = ConnectionManager()