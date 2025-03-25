from fastapi import APIRouter, Depends, status, Path, Query, Body

from models.quiz import tbl_user
from router.v1.quiz.protocol import Req_Quiz_Update, Req_QuizCreate, Req_QuizSubmit, Res_Quiz_Update, Res_QuizCreate, Res_QuizDelete, Res_QuizList, Res_QuizDetail, Res_QuizStart, Res_QuizSession, Res_QuizSubmit, Res_QuizSaveAnswer, Req_QuizSaveAnswer
from router.v1.validator.dependencies import RemoveNoneResponse
from services.quiz_service import QuizService
from middleware.auth import get_current_admin_user, get_current_user

router = APIRouter(prefix="/quiz", tags=["퀴즈"], responses={404: {"description": "Not found"}})

@router.post(path="/create", response_model=Res_QuizCreate, summary="퀴즈 생성", description="퀴즈를 생성합니다.", status_code=status.HTTP_201_CREATED)
async def create_quiz(req: Req_QuizCreate, service: QuizService = Depends(), user: tbl_user = Depends(get_current_admin_user)):
    """
    관리자만 퀴즈를 생성할 수 있습니다.
    """
    return RemoveNoneResponse(await service.create_quiz(req, user))

# TODO 쿼리문으로 받자. 그럴려면 create시 select 받아야함.
@router.post("/update", response_model=Res_Quiz_Update, summary="퀴즈 수정", description="퀴즈를 수정합니다.", status_code=status.HTTP_200_OK)
async def update_quiz(req: Req_Quiz_Update, service: QuizService = Depends(), user: tbl_user = Depends(get_current_admin_user)):
    """
    관리자만 퀴즈를 수정할 수 있습니다.
    """
    return RemoveNoneResponse(await service.update_quiz(req, user))

@router.delete("/delete/{quiz_id}", response_model=Res_QuizDelete, summary="퀴즈 삭제", description="퀴즈를 삭제합니다.", status_code=status.HTTP_200_OK)
async def delete_quiz(quiz_id: int, service: QuizService = Depends(), user: tbl_user = Depends(get_current_admin_user)):
    """
    관리자만 퀴즈를 삭제할 수 있습니다.
    """
    return RemoveNoneResponse(await service.delete_quiz(quiz_id, user))

@router.get("/list/{page}/{page_size}", response_model=Res_QuizList, summary="퀴즈 목록 조회", description="퀴즈 목록을 조회합니다.", status_code=status.HTTP_200_OK)
async def get_quiz_list(page: int = Path(..., description="페이지 번호", ge=1), page_size: int = Path(..., description="페이지 크기", ge=1), service: QuizService = Depends(), user: tbl_user = Depends(get_current_admin_user)):
    """
    퀴즈 목록을 조회할 수 있습니다.
    """
    return RemoveNoneResponse(await service.get_quiz_list(page, page_size, user))

@router.get("/{quiz_id}", response_model=Res_QuizDetail, summary="퀴즈 상세 조회", description="퀴즈 상세 조회", status_code=status.HTTP_200_OK)
async def get_quiz_detail(quiz_id: int = Path(..., description="퀴즈 ID", ge=1), page: int = Query(1, description="페이지 번호", ge=1), service: QuizService = Depends(), user: tbl_user = Depends(get_current_user)):
    """
    퀴즈 상세 정보를 조회합니다.
    
    - **quiz_id**: 조회할 퀴즈 ID
    - **page**: 문제 페이지 번호 (기본값: 1)
    """
    return RemoveNoneResponse(await service.get_quiz_detail(quiz_id, page, user))

@router.post("/{quiz_id}/start", response_model=Res_QuizStart, summary="퀴즈 응시 시작", description="퀴즈 응시를 시작합니다.", status_code=status.HTTP_200_OK)
async def start_quiz(quiz_id: int = Path(..., description="퀴즈 ID", ge=1), service: QuizService = Depends(), user: tbl_user = Depends(get_current_user)):
    """
    퀴즈 응시를 시작합니다.
    
    - **quiz_id**: 응시할 퀴즈 ID
    """
    return RemoveNoneResponse(await service.start_quiz(quiz_id, user))

@router.get("/session/{session_id}", response_model=Res_QuizSession, summary="퀴즈 응시 상태 조회", description="퀴즈 응시 상태를 조회합니다.", status_code=status.HTTP_200_OK)
async def get_quiz_session(session_id: str = Path(..., description="세션 ID"), service: QuizService = Depends(), user: tbl_user = Depends(get_current_user)):
    """
    퀴즈 응시 상태를 조회합니다.
    
    - **session_id**: 조회할 세션 ID
    """
    return RemoveNoneResponse(await service.get_quiz_session(session_id, user))

@router.post("/session/answer", response_model=Res_QuizSaveAnswer, summary="퀴즈 답안 저장", description="퀴즈 답안을 저장합니다.", status_code=status.HTTP_200_OK)
async def save_quiz_answer(req: Req_QuizSaveAnswer = Body(...), service: QuizService = Depends(), user: tbl_user = Depends(get_current_user)):
    """
    퀴즈 답안을 저장합니다.
    
    - **session_id**: 세션 ID
    - **question_id**: 문제 ID
    - **choice_id**: 선택지 ID
    """
    return RemoveNoneResponse(await service.save_quiz_answer(req, user))

@router.post("/session/submit", response_model=Res_QuizSubmit, summary="퀴즈 답안 제출", description="퀴즈 답안을 제출하고 채점합니다.", status_code=status.HTTP_200_OK)
async def submit_quiz(req: Req_QuizSubmit = Body(...), service: QuizService = Depends(), user: tbl_user = Depends(get_current_user)):
    """
    퀴즈 답안을 제출하고 채점합니다.
    
    - **session_id**: 세션 ID
    - **answers**: 답안 (문제 ID: 선택지 ID)
    """
    return RemoveNoneResponse(await service.submit_quiz(req, user))
