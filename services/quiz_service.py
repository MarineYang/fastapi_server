from typing import List, Optional, Dict, Any, Tuple
from fastapi import Depends, HTTPException
from datetime import datetime
import random

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from commons.utils.enums import ErrorType
from crud.quiz_crud import IQuizCRUD, QuizCRUD
from db.database import DB_SESSION_MNG
from models.quiz import tbl_user
from router.v1.quiz.protocol import Choice, Question, Req_Quiz_Update, Req_QuizCreate, Req_QuizSaveAnswer, Req_QuizSubmit,  Res_Quiz_Update, Res_QuizCreate, Res_QuizDelete, Res_QuizList, Res_QuizDetail, QuizListItem, Res_QuizSaveAnswer, Res_QuizSession, Res_QuizStart, Res_QuizSubmit
from sqlalchemy.ext.asyncio import AsyncSession
# from schemas.quiz import QuizCreate, QuizUpdate, QuestionCreate, Quiz, Question, Choice

security = HTTPBearer()

class QuizService:
    def __init__(self, 
                 credentials: HTTPAuthorizationCredentials = Depends(security),
                 quiz_crud: IQuizCRUD = Depends(QuizCRUD),
                 ):
        self.credentials = credentials
        self.quiz_crud = quiz_crud 
    async def create_quiz(self, req: Req_QuizCreate, user: tbl_user) -> Res_QuizCreate:
        res = Res_QuizCreate()

        if not user.is_admin:
            res.result.SetResult(ErrorType.NOT_ADMIN)
            return res

        quiz, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.create_quiz(s, req, user.id))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(ErrorType.DB_RUN_FAILED)
            return res
        
        default_choices = [Choice(text="임시 선택지 1", is_correct=True), Choice(text="임시 선택지 2", is_correct=False)]
        
        res.quiz_id = quiz.id
        res.user_id = user.id
        res.title = quiz.title
        res.description = quiz.description
        res.is_randomized_questions = quiz.is_randomized_questions
        res.is_randomized_choices = quiz.is_randomized_choices
        res.selected_questions = quiz.selected_questions
        res.questions = []
        
        for question in quiz.questions:
            question_data = {
                "id": question.id,
                "question_text": question.question_text,
                "choices": []
            }   
            
            # 기존 선택지가 있으면 기본 선택지를 대체
            if hasattr(question, 'choices') and question.choices:
                choices_list = []
                for choice in question.choices:
                    choice_data = {
                        "id": choice.id,
                        "text": choice.content,
                        "is_correct": choice.is_correct
                    }
                    choices_list.append(choice_data)
                
                # 선택지가 2개 이상이면 기본 선택지 대신 사용
                if len(choices_list) >= 2:
                    question_data["choices"] = choices_list
            
            res.questions.append(question_data)
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res
    
    async def update_quiz(self, req: Req_Quiz_Update, user: tbl_user) -> Res_Quiz_Update:
        res = Res_Quiz_Update()

        if not user.is_admin:
            res.result.SetResult(ErrorType.NOT_ADMIN)
            return res

        # 퀴즈 존재 확인
        quiz, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.get_quiz_by_id(s, req.id))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(ErrorType.DB_RUN_FAILED)
            return res
        
        if not quiz:
            res.result.SetResult(ErrorType.QUIZ_NOT_FOUND)
            return res
        
        err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.update_quiz(s, quiz, req))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(ErrorType.DB_RUN_FAILED)
            return res  
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res

    async def delete_quiz(self, quiz_id: int, user: tbl_user) -> Res_QuizDelete:
        res = Res_QuizDelete()

        if not user.is_admin:
            res.result.SetResult(ErrorType.NOT_ADMIN)
            return res

        # 퀴즈 존재 확인
        err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.delete_quiz(s, quiz_id, user.id))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(err_type)
            return res
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res
    
    async def get_quiz_list(self, page: int, page_size: int, user: tbl_user) -> Res_QuizList:
        """퀴즈 목록을 조회합니다."""
        res = Res_QuizList()
        
        # 페이지네이션 파라미터 사용
        quiz_data, err_type = await DB_SESSION_MNG.execute_lambda(
            lambda s: self.quiz_crud.get_quiz_list(s, page, page_size, user)
        )
        
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(ErrorType.DB_RUN_FAILED)
            return res
        
        # 응답 설정
        res.total_quizzes = quiz_data.get("total_quizzes", 0)
        res.page = page
        res.page_size = page_size
        res.total_pages = quiz_data.get("total_pages", 0)
        
        # 퀴즈 목록 설정
        res.quizzes = []
        for quiz_data_item in quiz_data.get("quizzes", []):
            quiz_item = QuizListItem(
                quiz_id=quiz_data_item.get("quiz_id"),
                title=quiz_data_item.get("title"),
                description=quiz_data_item.get("description"),
                total_questions=quiz_data_item.get("total_questions"),
                selected_questions=quiz_data_item.get("selected_questions"),
                is_randomized_questions=quiz_data_item.get("is_randomized_questions"),
                is_randomized_choices=quiz_data_item.get("is_randomized_choices"),
                created_at=quiz_data_item.get("created_at"),
                updated_at=quiz_data_item.get("updated_at")
            )
            
            # 관리자에게만 표시할 정보
            if user.is_admin and "created_by" in quiz_data_item:
                quiz_item.created_by = quiz_data_item.get("created_by")
            
            # 사용자에게만 표시할 정보
            if not user.is_admin and "status" in quiz_data_item:
                quiz_item.status = quiz_data_item.get("status")
            
            res.quizzes.append(quiz_item)
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res

    async def get_quiz_detail(self, quiz_id: int, page: int, user: tbl_user) -> Res_QuizDetail:
        """퀴즈 상세 정보를 조회합니다."""
        res = Res_QuizDetail()
        
        # 퀴즈 상세 정보 조회
        quiz_data, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.get_quiz_detail(s, quiz_id, page, user))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(err_type)
            return res
        
        if not quiz_data:
            res.result.SetResult(ErrorType.QUIZ_NOT_FOUND)
            return res
        
        # 기본 퀴즈 정보 설정
        res.quiz_id = quiz_data.get("quiz_id")
        res.title = quiz_data.get("title")
        res.description = quiz_data.get("description")
        res.is_randomized_questions = quiz_data.get("is_randomized_questions")
        res.is_randomized_choices = quiz_data.get("is_randomized_choices")
        res.selected_questions = quiz_data.get("selected_questions")
        res.total_questions = quiz_data.get("total_questions")
        res.created_at = quiz_data.get("created_at")
        res.updated_at = quiz_data.get("updated_at")
        res.created_by = quiz_data.get("created_by")
        
        # 페이징 정보 설정
        res.current_page = page
        res.total_pages = quiz_data.get("total_pages")
        res.questions_per_page = quiz_data.get("questions_per_page")
        
        # 문제 목록 설정
        res.questions = []
        for question_data in quiz_data.get("questions", []):
            question = {
                "id": question_data.get("id"),
                "question_text": question_data.get("question_text"),
                "choices": []
            }
            
            # 선택지 설정
            for choice_data in question_data.get("choices", []):
                choice = {
                    "id": choice_data.get("id"),
                    "text": choice_data.get("text"),
                    "is_correct": choice_data.get("is_correct") if user.is_admin else None  # 관리자만 정답 확인 가능
                }
                question["choices"].append(choice)
            
            # 선택지 순서 랜덤화 (설정된 경우)
            if quiz_data.get("is_randomized_choices"):
                random.shuffle(question["choices"])
            
            res.questions.append(question)
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res
    
    async def start_quiz(self, quiz_id: int, user: tbl_user) -> Res_QuizStart:
        """퀴즈 응시를 시작합니다."""
        res = Res_QuizStart()
        
        if not user:
            res.result.SetResult(ErrorType.NOT_AUTHORIZED)
            return res
        
        # 퀴즈 응시 세션 시작
        session_data, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.start_quiz_session(s, quiz_id, user.id))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(err_type)
            return res
        
        if not session_data:
            res.result.SetResult(ErrorType.QUIZ_NOT_FOUND)
            return res
        
        # 응답 설정
        res.quiz_id = session_data.get("quiz_id")
        res.session_id = session_data.get("session_id")
        res.title = session_data.get("title")
        res.description = session_data.get("description")
        res.started_at = session_data.get("started_at")
        res.is_completed = session_data.get("is_completed")
        
        # 문제 목록 설정
        res.questions = []
        for question_data in session_data.get("questions", []):
            question = {
                "question_id": question_data.get("question_id"),
                "question_text": question_data.get("question_text"),
                "choices": question_data.get("choices", []),
                "selected_choice_id": question_data.get("selected_choice_id")
            }
            res.questions.append(question)
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res
    
    async def get_quiz_session(self, session_id: str, user: tbl_user) -> Res_QuizSession:
        """퀴즈 응시 세션 정보를 조회합니다."""
        res = Res_QuizSession()
        
        if not user:
            res.result.SetResult(ErrorType.NOT_AUTHORIZED)
            return res
        
        # 퀴즈 응시 세션 조회
        session_data, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.get_quiz_session(s, session_id, user.id))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(err_type)
            return res
        
        if not session_data:
            res.result.SetResult(ErrorType.SESSION_NOT_FOUND)
            return res
        
        # 응답 설정
        res.quiz_id = session_data.get("quiz_id")
        res.session_id = session_data.get("session_id")
        res.title = session_data.get("title")
        res.description = session_data.get("description")
        res.started_at = session_data.get("started_at")
        res.is_completed = session_data.get("is_completed")
        res.completed_at = session_data.get("completed_at")
        res.score = session_data.get("score")
        
        # 문제 목록 설정
        res.questions = []
        for question_data in session_data.get("questions", []):
            question = {
                "question_id": question_data.get("question_id"),
                "question_text": question_data.get("question_text"),
                "choices": question_data.get("choices", []),
                "selected_choice_id": question_data.get("selected_choice_id")
            }
            res.questions.append(question)
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res
    
    async def save_quiz_answer(self, req: Req_QuizSaveAnswer, user: tbl_user) -> Res_QuizSaveAnswer:
        """퀴즈 답안을 저장합니다."""
        res = Res_QuizSaveAnswer()
        
        if not user:
            res.result.SetResult(ErrorType.NOT_AUTHORIZED)
            return res
        
        # 퀴즈 답안 저장
        result, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.quiz_crud.save_answer(s, req, user.id))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(err_type)
            return res
        
        if not result:
            res.result.SetResult(ErrorType.QUIZ_SESSION_NOT_FOUND)
            return res
        
        # 응답 설정
        res.session_id = result.get("session_id")
        res.question_id = result.get("question_id")
        res.choice_id = result.get("choice_id")
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res
    
    async def submit_quiz(self, req: Req_QuizSubmit, user: tbl_user) -> Res_QuizSubmit:
        """퀴즈 답안을 제출하고 채점합니다."""
        res = Res_QuizSubmit()
        
        if not user:
            res.result.SetResult(ErrorType.NOT_AUTHORIZED)
            return res
        
        # 답안 리스트를 딕셔너리로 변환
        answers_dict = {answer.question_id: answer.choice_id for answer in req.answers}
        
        # 퀴즈 답안 제출 및 채점
        result, err_type = await DB_SESSION_MNG.execute_lambda(
            lambda s: self.quiz_crud.submit_quiz(s, req.session_id, answers_dict, user.id)
        )
        
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(err_type)
            return res
        
        if not result:
            res.result.SetResult(ErrorType.QUIZ_SESSION_NOT_FOUND)
            return res
        
        # 응답 설정
        res.quiz_id = result.get("quiz_id")
        res.session_id = result.get("session_id")
        res.title = result.get("title")
        res.total_questions = result.get("total_questions")
        res.correct_answers = result.get("correct_answers")
        res.score = result.get("score")
        res.started_at = result.get("started_at")
        res.completed_at = result.get("completed_at")
        
        # 문제 및 결과 목록 설정
        res.questions = []
        for question_data in result.get("questions", []):
            question = {
                "question_id": question_data.get("question_id"),
                "question_text": question_data.get("question_text"),
                "selected_choice_id": question_data.get("selected_choice_id"),
                "selected_choice_text": question_data.get("selected_choice_text"),
                "correct_choice_id": question_data.get("correct_choice_id"),
                "correct_choice_text": question_data.get("correct_choice_text"),
                "is_correct": question_data.get("is_correct")
            }
            res.questions.append(question)
        
        res.result.SetResult(ErrorType.SUCCESS)
        return res