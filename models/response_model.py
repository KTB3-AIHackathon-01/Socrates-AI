from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# Chat Models
class ChatRequest(BaseModel):
    user_input: List[str] = Field(None, description="사용자 입력(Spring에서 전달, 전체 메시지를 배열로 받음)")


class ChatInitResponse(BaseModel):
    user_facing_message: str
    checkpoints: list[str]


class ChatQNAResponse(BaseModel):
    user_facing_message: str
    is_stuck: bool
    next_action: str


class ReportRequest(BaseModel):
    user_input: List[List[str]] = Field(None, description="2D 배열: [[세션1 메시지들...], [세션2 메시지들...]]")


# Learning Report Models
class LearningSessionSummary(BaseModel):
    overall_progress_score: float = Field(..., description="전체 학습 진행도 점수 (0-1)")
    overall_difficulty_score: float = Field(..., description="전체 난이도 점수 (0-1)")
    mastery_ratio: float = Field(..., description="학습 숙달도 비율 (0-1)")


class ConceptMastery(BaseModel):
    concept: str = Field(..., description="개념명")
    importance: str = Field(default="medium", description="개념의 중요도 (high/medium/low)")
    status: str = Field(..., description="상태 (learning/partial/proficient/mastered)")
    understanding_score: float = Field(..., description="이해도 점수 (0-1)")
    breakthrough: bool = Field(default=False, description="개념 파악 여부")
    evidence_question: Optional[str] = Field(default=None, description="증거 질문")
    learning_activity_time: str = Field(default="", description="학습 활동 시간 (ISO 형식)")


class StuckConcept(BaseModel):
    concept: str = Field(..., description="어려워하는 개념")
    frequency: int = Field(..., description="막힌 횟수")
    root_cause: str = Field(..., description="원인 분석")


class LearningDifficulty(BaseModel):
    primary_root_cause: str = Field(..., description="주요 원인 (prerequisite_gap/conceptual_misconception/learning_strategy_mismatch)")
    secondary_root_cause: Optional[str] = Field(default=None, description="보조 원인")
    stuck_concepts: List[StuckConcept] = Field(default_factory=list, description="막힌 개념들")


class QuestionTypeRatio(BaseModel):
    definition: float = Field(..., description="정의 질문 비율")
    mechanism: float = Field(..., description="작동 원리 질문 비율")
    comparison: float = Field(..., description="비교 질문 비율")


class LearningBehavior(BaseModel):
    question_depth_score: float = Field(..., description="질문 깊이 점수 (0-1)")
    question_type_ratio: QuestionTypeRatio = Field(..., description="질문 유형 비율")
    concept_link_score: float = Field(..., description="개념 연결 점수 (0-1)")
    confirmation_question_ratio: float = Field(..., description="확인 질문 비율 (0-1)")


class InstructionalGuidance(BaseModel):
    next_focus_concepts: List[str] = Field(..., description="다음 학습할 개념들")
    teaching_recommendations: List[str] = Field(..., description="교수 권장사항들")
    next_session_goal: str = Field(..., description="다음 세션 목표")
    recommended_practice: str = Field(..., description="권장 연습")


class AnalysisResponse(BaseModel):
    user_id: str = Field(default="anonymous", description="사용자 ID")
    learning_summary: LearningSessionSummary = Field(..., description="학습 종합 분석")
    concept_mastery: List[ConceptMastery] = Field(..., description="개념별 숙달도")
    learning_difficulty: LearningDifficulty = Field(..., description="학습 어려움 분석")
    learning_behavior: LearningBehavior = Field(..., description="학습 행동 분석")
    instructional_guidance: InstructionalGuidance = Field(..., description="교수적 가이드")
    total_questions: int = Field(default=0, description="총 질문수")
    understanding_score: float = Field(default=0.0, description="이해도 점수")
    recent_activity: str = Field(default="", description="최근 활동 시간 (ISO 형식)")


class ReportResponse(BaseModel):
    user_facing_message: str = Field(..., description="사용자용 메시지")
    analysis: Optional[Dict[str, Any]] = Field(default=None, description="분석 결과")
