"""
xAI 구조화된 출력 테스트를 위한 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DifficultyLevel(str, Enum):
    """질문 난이도 레벨"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionCategory(str, Enum):
    """질문 카테고리"""
    BASIC_INFO = "기본정보"
    DETAILS = "세부사항"
    ANALYSIS = "분석"
    APPLICATION = "적용"


class Question(BaseModel):
    """생성된 질문을 나타내는 모델"""
    question: str = Field(description="문서 내용을 기반으로 생성된 질문")
    category: QuestionCategory = Field(description="질문의 카테고리")
    difficulty: DifficultyLevel = Field(description="질문의 난이도")


class QuestionsResponse(BaseModel):
    """여러 질문들을 담는 응답 모델"""
    questions: List[Question] = Field(
        description="생성된 질문들의 리스트", 
        min_items=3, 
        max_items=10
    )
    total_count: int = Field(description="생성된 총 질문 수")
    
    def model_post_init(self, __context):
        """total_count를 자동으로 설정"""
        self.total_count = len(self.questions)


class SimpleResponse(BaseModel):
    """간단한 테스트용 응답 모델"""
    message: str = Field(description="응답 메시지")
    timestamp: str = Field(description="생성 시간")
    confidence: float = Field(description="응답 신뢰도 (0.0-1.0)", ge=0.0, le=1.0)


class TestUserProfile(BaseModel):
    """사용자 프로필 테스트용 모델"""
    name: str = Field(description="사용자 이름")
    age: int = Field(description="나이", gt=0, le=120)
    interests: List[str] = Field(description="관심사 목록")
    location: Optional[str] = Field(description="위치", default=None)