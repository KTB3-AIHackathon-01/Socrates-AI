import os, sys, uvicorn, asyncio
from typing import Annotated
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional
from uuid import uuid4
from graph.graph import chat_init, chat_qna
from graph.report import make_report


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
class ChatInitModel(BaseModel):
  session_id: str = Field(..., description="세션 ID")
  topic: str = Field(..., description="학습할 주제(단어 혹은 문장 형태)")
class ChatQNAModel(BaseModel):
  session_id: str = Field(..., description="세션 ID")
  user_input: str = Field(..., description="사용자 입력(Spring에서 받음)")
  topic: str = Field(..., description="학습할 주제(단어 혹은 문장 형태)")
class ReportModel(BaseModel):
  session_id: str

class ChatInitResponse(BaseModel):
  brief_reaction: str
  user_facing_message: str
  checkpoints: list[str]

class ChatQNAResponse(BaseModel):
  user_facing_message: str
  is_stuck: bool
  next_action: str

@app.post("/api/chat_init")
async def chat_init_api(data: Annotated[ChatInitModel, Body(embed=True)]):
  """
  첫 채팅시 사용하는 엔드포인트\n
  * 테스트 시에 session_id 는 아무거나 넣어도 동작합니다.
  """
  result = await chat_init(data.topic)
  response = ChatInitResponse(
    brief_reaction=result.get("brief_reaction", ""),
    user_facing_message=result.get("user_facing_message", ""),
    checkpoints=result.get("checkpoints", [])
  )
  return JSONResponse(content={"success": True, "data": response.model_dump()})

@app.post("/api/chat_qna")
async def chat_qna_api(data: ChatQNAModel):
  result = await chat_qna(data.session_id, data.user_input, data.topic)
  response = ChatQNAResponse(
    user_facing_message=result.get("user_facing_message", result.get("ai_response", "")),
    is_stuck=result.get("is_stuck", False),
    next_action=result.get("next_action", "continue")
  )
  return JSONResponse(content={"success": True, "data": response.model_dump()})

# @app.post("/api/report")
# async def report_api(data: ReportModel):
#   report_content = await make_report(data.session_id)
#   return JSONResponse(content={"success": True, "report": report_content})

@app.get("/health")
async def health_check():
  """API 헬스 체크 엔드포인트"""
  return JSONResponse(content={
    "status": "healthy",
    "service": "Socratic Learning API",
    "version": "1.0.0"
  })

@app.get("/")
async def root():
  return JSONResponse(content={"success": True, "message": "Welcome to Socratic Learning API"})


if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)