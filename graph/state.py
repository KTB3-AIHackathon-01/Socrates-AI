from typing import TypedDict, Optional, List
from datetime import datetime

class Message(TypedDict):
  role: str  # "user" or "assistant"
  content: str
  timestamp: datetime

class Checkpoint(TypedDict):
  turn: int
  phase: str
  progress: float
  misconceptions: List[str]
  attempt_count: int
  saved_at: datetime

class LearningState(TypedDict):
  # 기본 정보
  session_id: str
  topic: str
  
  # 대화 정보
  messages: List[Message]
  conversation_phase: str  # "initial" | "ongoing" | "closing"
  
  # 학습 추적
  progress: float  # 0-100
  attempt_count: int  # 같은 질문 시도 횟수
  misconceptions: List[str]  # 발견된 오개념들
  difficulty_level: str  # "basic" | "intermediate" | "advanced"
  
  # 시스템 정보
  system_prompt: str
  current_question: Optional[str]
  
  # 체크포인트
  checkpoints: List[Checkpoint]
  should_save_checkpoint: bool