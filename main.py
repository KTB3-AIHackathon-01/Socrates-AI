import os, sys, uvicorn, asyncio
from typing import Annotated, List
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from typing import Optional
from uuid import uuid4
from graph.graph import chat_init, chat_qna
from graph.report import make_report, make_daily_report
from models import ChatRequest, ChatInitResponse, ChatQNAResponse, ReportRequest


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

@app.post("/chat")
async def chat_api(data: Annotated[ChatRequest, Body(embed=True)]):
  """
  채팅시 사용하는 엔드포인트
  """

  is_completed = False

  if len(data.user_input) > 20:
    is_completed = True
    return JSONResponse(content={"success": True, "is_completed": is_completed, "data": None})
  
  if len(data.user_input) < 2:
    result = await chat_init(data.user_input[0])
    response = ChatInitResponse(
      user_facing_message=f"{result.get("brief_reaction", "")} {result.get("user_facing_message", "")}",
      checkpoints=result.get("checkpoints", [])
    )
    is_completed = False
  else:
    result = await chat_qna(data.user_input)
    response = ChatQNAResponse(
      user_facing_message=result.get("user_facing_message", ""),
      is_stuck=result.get("is_stuck", False),
      next_action=result.get("next_action", "")
    )
    is_completed = result.get("is_stuck", False)

  return JSONResponse(content={"success": True, "is_completed": is_completed, "data": response.model_dump()})

@app.post("/chat/report")
async def report_api(data: Annotated[ChatRequest, Body(embed=True)]):
  report_content = await make_report(data.user_input)
  return JSONResponse(content={"success": True, "report": report_content})

@app.post("/report/daily")
async def report_daily_api(data: Annotated[ReportRequest, Body(embed=True)]):
  """일일 학습 세션 분석 리포트 엔드포인트"""
  analysis_result = await make_daily_report(data.user_input)
  return JSONResponse(content={"success": True, "data": analysis_result})

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