from pydantic import BaseModel
from typing import Optional, Literal

class ClientMessage(BaseModel):
  action: Literal["start", "respond", "close"]
  topic: Optional[str] = None
  session_id: Optional[str] = None
  answer: Optional[str] = None

class ServerEvent(BaseModel):
  event: Literal["question", "processing", "checkpoint", "session_end", "error"]
  session_id: str
  question: Optional[str] = None
  phase: Optional[str] = None
  progress: Optional[float] = None
  checkpoint_data: Optional[dict] = None
  summary: Optional[str] = None
  final_report: Optional[dict] = None
  error_message: Optional[str] = None
  error_code: Optional[str] = None