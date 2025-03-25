from typing import List, Optional, Dict, Any, Union
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from datetime import datetime
from commons.models.gmodel import Req_WebPacketProtocol, Res_WebPacketProtocol, WebPacketProtocol


class QuizProtocol(WebPacketProtocol):
    title: str = Field(..., description="퀴즈 제목")
    description: str = Field(..., description="퀴즈 설명")


class Choice(BaseModel):
    text: str = Field(..., description="선택지 내용")
    is_correct: bool = Field(..., description="정답 여부")

# 문제 모델
class Question(BaseModel):
    question_text: str = Field(..., description="문제 내용")
    choices: list[Choice] = Field(..., description="선택지 목록")

    @validator('choices')
    def validate_choices(cls, v):
        if len(v) < 2:
            raise HTTPException(status_code=400, detail='최소 2개의 선택지가 필요합니다')
        
        correct_count = sum(1 for choice in v if choice.is_correct)
        if correct_count != 1:
            raise HTTPException(status_code=400, detail='정확히 하나의 정답이 있어야 합니다')
        
        return v
    

correct_example = [
    [{
        "question_text": "다음 중 인터프리터 언어는?",
        "choices": [
            {"text": "파이썬", "is_correct": True},
            {"text": "C++", "is_correct": False},
            {"text": "Java", "is_correct": False},
            {"text": "Swift", "is_correct": False}
        ]
    },
    {
        "question_text": "내가 제일 좋아하는 색깔은?",
        "choices": [
            {"text": "빨강", "is_correct": False},
            {"text": "초록", "is_correct": False},
            {"text": "파랑", "is_correct": True},
            {"text": "노랑", "is_correct": False}
        ]
    }]
]

update_example = [
    [{
        "id": 1,
        "question_text": "다음 중 인터프리터 언어는?",
        "choices": [
            {"id": 1, "text": "파이썬", "is_correct": True},
            {"id": 2, "text": "C++", "is_correct": False},
            {"id": 3, "text": "Java", "is_correct": False},
            {"id": 4, "text": "Swift", "is_correct": False}
        ]
    },
    {
        "id": 2,
        "question_text": "내가 제일 좋아하는 색깔은?",
        "choices": [
            {"id": 1, "text": "빨강", "is_correct": False},
            {"id": 2, "text": "초록", "is_correct": False},
            {"id": 3, "text": "파랑", "is_correct": True},
            {"id": 4, "text": "노랑", "is_correct": False}
        ]
    }]
]


class Req_QuizCreate(Req_WebPacketProtocol):
    title: str = Field(..., description="퀴즈 제목", example="프로그래밍 언어 퀴즈")
    description: str = Field(..., description="퀴즈 설명", example="다양한 프로그래밍 언어에 관한 퀴즈입니다.")
    is_randomized_questions: bool = Field(False, description="문제 순서 랜덤 여부", example=True)
    is_randomized_choices: bool = Field(False, description="선택지 순서 랜덤 여부", example=True)
    selected_questions: int = Field(10, description="출제할 문제 수", example=10)
    questions: list[Question] = Field(..., description="문제 목록", examples=correct_example)
    
    

class Res_QuizCreate(Res_WebPacketProtocol):
    quiz_id: int = Field(0, description="퀴즈 ID")
    user_id: int = Field(0, description="사용자 ID")
    title: str = Field("", description="퀴즈 제목", example="프로그래밍 언어 퀴즈")
    description: str = Field("", description="퀴즈 설명", example="다양한 프로그래밍 언어에 관한 퀴즈입니다.")
    is_randomized_questions: bool = Field(False, description="문제 순서 랜덤 여부", example=True)
    is_randomized_choices: bool = Field(False, description="선택지 순서 랜덤 여부", example=True)
    selected_questions: int = Field(10, description="출제할 문제 수", example=10)
    questions: list[Question] = Field([], description="문제 목록", examples=correct_example)

class Req_Quiz_Update(Req_WebPacketProtocol):
    id: int = Field(..., description="퀴즈 ID")
    title: str = Field(..., description="퀴즈 제목")
    description: str = Field(..., description="퀴즈 설명")
    is_randomized_questions: bool = Field(False, description="문제 순서 랜덤 여부")
    questions: list[Question] = Field([], description="문제 목록", examples=update_example)

class Res_Quiz_Update(Res_WebPacketProtocol):
    pass

class Res_Question(Res_WebPacketProtocol):
    id: int = Field(..., description="문제 ID")
    question_text: str = Field(..., description="문제 내용")
    choices: List[Choice] = Field(..., description="선택지 목록")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

class Res_QuizInfo(QuizProtocol):
    is_randomized_questions: bool = Field(False, description="문제 순서 랜덤 여부")
    questions: List[Res_Question] = Field([], description="문제 목록")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

# 퀴즈 수정 요청
class Req_QuizUpdate(Req_WebPacketProtocol):
    id: int = Field(..., description="퀴즈 ID")
    title: str = Field(..., description="퀴즈 제목")
    description: str = Field(..., description="퀴즈 설명")
    is_randomized_questions: bool = Field(False, description="문제 순서 랜덤 여부")
    questions: List[Question] = Field([], description="문제 목록")


# 퀴즈 삭제 응답
class Res_QuizDelete(Res_WebPacketProtocol):
    pass

# 퀴즈 목록 조회 요청
# 퀴즈 목록 항목 응답 모델
class QuizListItem(BaseModel):
    quiz_id: int = Field(..., description="퀴즈 ID")
    title: str = Field(..., description="퀴즈 제목")
    description: Optional[str] = Field(None, description="퀴즈 설명")
    total_questions: int = Field(..., description="총 문제 수")
    selected_questions: int = Field(..., description="출제할 문제 수")
    is_randomized_questions: bool = Field(..., description="문제 순서 랜덤 여부")
    is_randomized_choices: bool = Field(..., description="선택지 순서 랜덤 여부")
    created_at: datetime = Field(..., description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")
    
    # 관리자에게만 표시되는 필드
    created_by: Optional[str] = Field(None, description="생성자")
    
    # 사용자에게만 표시되는 필드
    status: Optional[str] = Field(None, description="퀴즈 상태 (not_attempted, in_progress, completed)")
    
    # 퀴즈 목록 응답 모델
class Res_QuizList(Res_WebPacketProtocol):
    """퀴즈 목록 조회 응답"""
    total_quizzes: int = Field(0, description="총 퀴즈 수")
    page: int = Field(1, description="현재 페이지")
    page_size: int = Field(10, description="페이지당 항목 수")
    total_pages: int = Field(0, description="총 페이지 수")
    quizzes: List[QuizListItem] = Field([], description="퀴즈 목록")
    
class Res_QuizDetail(Res_WebPacketProtocol):
    """퀴즈 상세 조회 응답"""
    quiz_id: Optional[int] = Field(None, description="퀴즈 ID")
    title: Optional[str] = Field(None, description="퀴즈 제목")
    description: Optional[str] = Field(None, description="퀴즈 설명")
    is_randomized_questions: Optional[bool] = Field(None, description="문제 순서 랜덤 여부")
    is_randomized_choices: Optional[bool] = Field(None, description="선택지 순서 랜덤 여부")
    selected_questions: Optional[int] = Field(None, description="출제할 문제 수")
    total_questions: Optional[int] = Field(None, description="총 문제 수")
    created_at: Optional[datetime] = Field(None, description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")
    created_by: Optional[str] = Field(None, description="생성자")
    
    # 페이징 정보
    current_page: int = Field(1, description="현재 페이지")
    total_pages: int = Field(1, description="총 페이지 수")
    questions_per_page: int = Field(10, description="페이지당 문제 수")
    
    # 문제 목록
    questions: list[Question] = Field(default_factory=list, description="문제 목록")
    
# 퀴즈 응시 시작 응답
class QuizSessionChoice(BaseModel):
    """퀴즈 응시 선택지"""
    choice_id: int = Field(..., description="선택지 ID")
    text: str = Field(..., description="선택지 내용")

class QuizSessionQuestion(BaseModel):
    """퀴즈 응시 문제"""
    question_id: int = Field(..., description="문제 ID")
    question_text: str = Field(..., description="문제 내용")
    choices: List[QuizSessionChoice] = Field(..., description="선택지 목록")
    selected_choice_id: Optional[int] = Field(None, description="사용자가 선택한 선택지 ID")

class Res_QuizStart(Res_WebPacketProtocol):
    """퀴즈 응시 시작 응답"""
    quiz_id: Optional[int] = Field(None, description="퀴즈 ID")
    session_id: Optional[str] = Field(None, description="세션 ID")
    title: Optional[str] = Field(None, description="퀴즈 제목")
    description: Optional[str] = Field(None, description="퀴즈 설명")
    questions: List[QuizSessionQuestion] = Field(default_factory=list, description="문제 목록")
    started_at: Optional[datetime] = Field(None, description="응시 시작 시간")
    is_completed: bool = Field(False, description="완료 여부")

# 답안 항목 구조체
class QuizAnswer(BaseModel):
    """퀴즈 답안 항목"""
    question_id: int = Field(..., description="문제 ID")
    choice_id: int = Field(..., description="선택지 ID")

# 퀴즈 답안 제출 요청
class Req_QuizSubmit(BaseModel):
    """퀴즈 답안 제출 요청"""
    session_id: str = Field(..., description="세션 ID")
    answers: list[QuizAnswer] = Field(..., description="답안 목록")

# 퀴즈 답안 제출 응답
class QuizResultQuestion(BaseModel):
    """퀴즈 결과 문제"""
    question_id: int = Field(..., description="문제 ID")
    question_text: str = Field(..., description="문제 내용")
    selected_choice_id: Optional[int] = Field(None, description="사용자가 선택한 선택지 ID")
    selected_choice_text: Optional[str] = Field(None, description="사용자가 선택한 선택지 내용")
    correct_choice_id: int = Field(..., description="정답 선택지 ID")
    correct_choice_text: str = Field(..., description="정답 선택지 내용")
    is_correct: bool = Field(..., description="정답 여부")

class Res_QuizSubmit(Res_WebPacketProtocol):
    """퀴즈 답안 제출 응답"""
    quiz_id: Optional[int] = Field(None, description="퀴즈 ID")
    session_id: Optional[str] = Field(None, description="세션 ID")
    title: Optional[str] = Field(None, description="퀴즈 제목")
    total_questions: Optional[int] = Field(None, description="총 문제 수")
    correct_answers: Optional[int] = Field(None, description="정답 수")
    score: Optional[float] = Field(None, description="점수 (100점 만점)")
    started_at: Optional[datetime] = Field(None, description="응시 시작 시간")
    completed_at: Optional[datetime] = Field(None, description="응시 완료 시간")
    questions: list[QuizResultQuestion] = Field(default_factory=list, description="문제 및 결과 목록")

# 퀴즈 응시 상태 조회 응답
class Res_QuizSession(Res_WebPacketProtocol):
    """퀴즈 응시 상태 조회 응답"""
    quiz_id: Optional[int] = Field(None, description="퀴즈 ID")
    session_id: Optional[str] = Field(None, description="세션 ID")
    title: Optional[str] = Field(None, description="퀴즈 제목")
    description: Optional[str] = Field(None, description="퀴즈 설명")
    questions: List[QuizSessionQuestion] = Field(default_factory=list, description="문제 목록")
    started_at: Optional[datetime] = Field(None, description="응시 시작 시간")
    is_completed: bool = Field(False, description="완료 여부")
    completed_at: Optional[datetime] = Field(None, description="응시 완료 시간")
    score: Optional[int] = Field(None, description="점수 (완료된 경우)")

# 퀴즈 답안 저장 요청
class Req_QuizSaveAnswer(BaseModel):
    """퀴즈 답안 저장 요청"""
    session_id: str = Field(..., description="세션 ID")
    question_id: int = Field(..., description="문제 ID")
    choice_id: int = Field(..., description="선택지 ID")

# 퀴즈 답안 저장 응답
class Res_QuizSaveAnswer(Res_WebPacketProtocol):
    """퀴즈 답안 저장 응답"""
    session_id: Optional[str] = Field(None, description="세션 ID")
    question_id: Optional[int] = Field(None, description="문제 ID")
    choice_id: Optional[int] = Field(None, description="선택지 ID")
    