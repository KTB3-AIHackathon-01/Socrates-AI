from fastapi import FastAPI, HTTPException
import os, sys, uvicorn
from utils.response import BaseResponse, DataResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from graph.graph import run_learning_session
# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 환경변수 로드
load_dotenv()

app = FastAPI()

# 요청 스키마
class StartSessionRequest(BaseModel):
  topic: str

class UserResponseRequest(BaseModel):
  session_id: str
  response: str

@app.get("/")
async def root():
  return BaseResponse(success=True, message="Welcome to Socratic Learning API")

@app.post("/session/start")
async def start_session(request: StartSessionRequest):
    """새로운 학습 세션 시작"""
    try:
        result = run_learning_session(request.topic)
        return DataResponse(
            success=True,
            data=result,
            message="학습 세션을 시작했습니다."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/response")
async def submit_response(request: UserResponseRequest):
    """사용자 응답 제출"""
    try:
        # TODO: 세션 상태 관리 및 응답 처리
        return DataResponse(
            success=True,
            data={"message": "응답을 처리했습니다."},
            message="성공"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """세션 조회"""
    try:
        # TODO: DB에서 세션 정보 조회
        return DataResponse(
            success=True,
            data={"session_id": session_id},
            message="세션 정보를 조회했습니다."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
  uvicorn.run("main:app", reload=True)