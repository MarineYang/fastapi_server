from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Dict
import uuid
from sqlalchemy import desc, func, or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from commons.utils.enums import ErrorType
from db.database import DB_SESSION_MNG
from router.v1.quiz.protocol import Choice, Req_Quiz_Update, Req_QuizCreate, Req_QuizSaveAnswer, Req_QuizSubmit, Res_QuizCreate
from models.quiz import tbl_choice, tbl_choice_session, tbl_question_session, tbl_quiz, tbl_question, tbl_quiz_attempt, tbl_quiz_session, tbl_user

class IQuizCRUD(ABC):
    @abstractmethod
    async def create_quiz(self, db: AsyncSession, quiz_data: Req_QuizCreate, user_id: int) -> Tuple[tbl_quiz, ErrorType]:
        pass

    @abstractmethod
    async def get_quiz_by_user_id(self, db: AsyncSession, user_id: int) -> Tuple[list[tbl_quiz], ErrorType]:
        pass

    @abstractmethod
    async def get_quiz_by_id(self, db: AsyncSession, quiz_id: int) -> Tuple[tbl_quiz, ErrorType]:
        pass

    @abstractmethod
    async def update_quiz(self, db: AsyncSession, quiz: tbl_quiz) -> ErrorType:
        pass

    @abstractmethod
    async def delete_quiz(self, db: AsyncSession, quiz_id: int, user_id: int) -> ErrorType:
        pass    
    
    @abstractmethod
    async def get_quiz_list(self, db: AsyncSession, page: int, page_size: int, user: tbl_user) -> Tuple[dict, ErrorType]:
        pass

    @abstractmethod
    async def get_quiz_detail(self, db: AsyncSession, quiz_id: int, page: int, user: tbl_user) -> Tuple[dict, ErrorType]:
        pass

    @abstractmethod
    async def start_quiz_session(self, db: AsyncSession, quiz_id: int, user_id: int) -> Tuple[dict, ErrorType]:
        pass

    @abstractmethod
    async def get_quiz_session(self, db: AsyncSession, session_id: str, user_id: int) -> Tuple[dict, ErrorType]:
        pass

    @abstractmethod
    async def save_answer(self, db: AsyncSession, req: Req_QuizSaveAnswer, user_id: int) -> Tuple[dict, ErrorType]:
        pass

    @abstractmethod
    async def submit_quiz(self, db: AsyncSession, session_id: str, answers: Dict[int, int], user_id: int) -> Tuple[dict, ErrorType]:
        pass



class QuizCRUD(IQuizCRUD):
    async def create_quiz(self, db: AsyncSession, req: Req_QuizCreate, user_id: int) -> Tuple[tbl_quiz, ErrorType]:
        try:
            quiz = tbl_quiz(
                title=req.title,
                description=req.description,
                user_id=user_id,
                selected_questions=req.selected_questions,
                is_randomized_questions=req.is_randomized_questions,
                is_randomized_choices=req.is_randomized_choices
            )
            db.add(quiz)
            await db.flush()

            if req.questions:
                for question_data in req.questions:
                    question = tbl_question(
                        quiz_id=quiz.id,
                        question_text=question_data.question_text,
                    )
                    db.add(question)
                    await db.flush()

                    for choice_data in question_data.choices:
                        choice = tbl_choice(
                            question_id=question.id,
                            content=choice_data.text,
                            is_correct=choice_data.is_correct
                        )
                        db.add(choice)
                        await db.flush()
            
            await db.commit()
            
            result = await db.execute(
                select(tbl_quiz)
                .options(
                    selectinload(tbl_quiz.questions)
                    .selectinload(tbl_question.choices)
                )
                .where(tbl_quiz.id == quiz.id)
            )
            loaded_quiz = result.scalars().first()
            
            return loaded_quiz, ErrorType.SUCCESS
        except Exception as e:
            print("db create quiz error :", e)
            await db.rollback()
            return None, ErrorType.DB_RUN_FAILED
        
    async def get_quiz_by_user_id(self, db: AsyncSession, user_id: int) -> Tuple[list[tbl_quiz], ErrorType]:
        try:
            result = await db.execute(select(tbl_quiz).where(tbl_quiz.user_id == user_id))
            quiz_list = result.scalars().all()
            return quiz_list, ErrorType.SUCCESS
        
        except Exception as e:
            print("db get quiz error :", e)
            return None, ErrorType.DB_RUN_FAILED
        
    async def get_quiz_by_id(self, db: AsyncSession, quiz_id: int) -> Tuple[tbl_quiz, ErrorType]:
        try:
            result = await db.execute(select(tbl_quiz).where(tbl_quiz.id == quiz_id))
            quiz = result.scalars().first()
            return quiz, ErrorType.SUCCESS
        except Exception as e:
            print("db get quiz error :", e)
            return None, ErrorType.DB_RUN_FAILED
        
    async def update_quiz(self, db: AsyncSession, origin_quiz: tbl_quiz, update_quiz: Req_Quiz_Update) -> ErrorType:
        try:
            # 2. 퀴즈 기본 정보 업데이트
            if update_quiz.title:
                origin_quiz.title = update_quiz.title
            if update_quiz.description is not None:
                origin_quiz.description = update_quiz.description
            
            # 3. 질문 업데이트
            if update_quiz.questions:
                # 3.1 기존 질문 ID 목록 가져오기
                result = await db.execute(select(tbl_question).where(tbl_question.quiz_id == origin_quiz.id))
                existing_questions = {q.id: q for q in result.scalars().all()}
                
                # 3.2 업데이트할 질문 ID 목록
                update_question_ids = [q.id for q in update_quiz.questions if q.id is not None]
                
                # 3.3 각 질문 처리
                for question_data in update_quiz.questions:
                    if question_data.id is not None and question_data.id in existing_questions:
                        # 기존 질문 업데이트
                        question = existing_questions[question_data.id]
                        question.question_text = question_data.question_text
                        
                        # 선택지 처리
                        await self._update_choices(db, question.id, question_data.choices)
                    else:
                        # 새 질문 추가
                        new_question = tbl_question(
                            quiz_id=origin_quiz.id,
                            question_text=question_data.question_text
                        )
                        db.add(new_question)
                        await db.flush()  # ID 생성을 위해 flush
                        
                        # 새 선택지 추가
                        if question_data.choices:
                            for choice_data in question_data.choices:
                                new_choice = tbl_choice(
                                    question_id=new_question.id,
                                    content=choice_data.text,
                                    is_correct=choice_data.is_correct
                                )
                                db.add(new_choice)
                
                # 3.4 삭제된 질문 처리 (요청에 포함되지 않은 기존 질문)
                for q_id, question in existing_questions.items():
                    if q_id not in update_question_ids:
                        await db.delete(question)  # cascade 옵션으로 연결된 선택지도 삭제
            
            # 4. 변경사항 저장
            await db.commit()
            return ErrorType.SUCCESS
        except Exception as e:
            print("db update quiz error :", e)

    async def _update_choices(self, db: AsyncSession, question_id: int, choices_data: list[Choice]) -> None:
            """
            질문의 선택지를 업데이트합니다.

            Args:
                db: 데이터베이스 세션
                question_id: 질문 ID
                choices_data: 업데이트할 선택지 데이터
            """
            # 1. 기존 선택지 가져오기
            result = await db.execute(select(tbl_choice).where(tbl_choice.question_id == question_id))
            existing_choices = {c.id: c for c in result.scalars().all()}

            # 2. 업데이트할 선택지 ID 목록
            update_choice_ids = [c.id for c in choices_data if c.id is not None]

            # 3. 각 선택지 처리
            for choice_data in choices_data:
                if choice_data.id is not None and choice_data.id in existing_choices:
                    # 기존 선택지 업데이트
                    choice = existing_choices[choice_data.id]
                    choice.content = choice_data.text
                    choice.is_correct = choice_data.is_correct
                else:
                    # 새 선택지 추가
                    new_choice = tbl_choice(
                        question_id=question_id,
                        content=choice_data.text,
                        is_correct=choice_data.is_correct
                    )
                    db.add(new_choice)
                    # 4. 삭제된 선택지 처리 (요청에 포함되지 않은 기존 선택지)
            for c_id, choice in existing_choices.items():
                if c_id not in update_choice_ids:
                    await db.delete(choice)

    async def delete_quiz(self, db: AsyncSession, quiz_id: int, user_id: int) -> ErrorType:
        """퀴즈를 삭제합니다."""
        try:
            # 퀴즈 조회
            query = select(tbl_quiz).where(
                and_(
                    tbl_quiz.id == quiz_id,
                    tbl_quiz.user_id == user_id
                )
            )
            result = await db.execute(query)
            quiz = result.scalars().first()
            
            if not quiz:
                return ErrorType.QUIZ_NOT_FOUND
            
            # 퀴즈 삭제
            await db.delete(quiz)
            await db.commit()
            
            return ErrorType.SUCCESS
            
        except Exception as e:
            print(f"Error deleting quiz: {e}")
            await db.rollback()
            return ErrorType.DB_RUN_FAILED

    async def get_quiz_list(self, db: AsyncSession, page: int, page_size: int, user: tbl_user) -> Tuple[dict, ErrorType]:
        """
        퀴즈 목록을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            page: 페이지 번호
            page_size: 페이지당 항목 수
            user: 사용자 정보
            
        Returns:
            퀴즈 목록 데이터, 오류 타입
        """
        try:
            # 기본 쿼리 구성 (퀴즈 생성자 정보 포함)
            query = select(tbl_quiz, tbl_user.username.label("created_by")) \
                .join(tbl_user, tbl_quiz.user_id == tbl_user.id)
            
            # 최신순 정렬
            query = query.order_by(desc(tbl_quiz.created_at))
            
            # 총 개수 조회
            count_query = select(func.count()).select_from(query.subquery())
            total_quizzes = await db.scalar(count_query) or 0
            
            # 페이징 적용
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            # 퀴즈 목록 조회
            result = await db.execute(query)
            quizzes_with_creator = result.all()
            
            # 응답 데이터 구성
            quizzes_data = []
            for quiz_row in quizzes_with_creator:
                quiz = quiz_row[0]  # tbl_quiz 객체
                created_by = quiz_row[1]  # username
                
                # 문제 수 조회
                question_count_query = select(func.count()).where(tbl_question.quiz_id == quiz.id)
                total_questions = await db.scalar(question_count_query) or 0
                
                # 기본 퀴즈 정보
                quiz_data = {
                    "quiz_id": quiz.id,
                    "title": quiz.title,
                    "description": quiz.description,
                    "total_questions": total_questions,
                    "selected_questions": quiz.selected_questions,
                    "is_randomized_questions": quiz.is_randomized_questions,
                    "is_randomized_choices": quiz.is_randomized_choices,
                    "created_at": quiz.created_at,
                    "updated_at": quiz.updated_at
                }
                
                # 관리자에게만 표시할 정보
                if user.is_admin:
                    quiz_data["created_by"] = created_by
                
                # 사용자에게만 표시할 정보
                if not user.is_admin:
                    # 응시 기록 조회
                    attempt_query = select(tbl_quiz_attempt).where(
                        tbl_quiz_attempt.quiz_id == quiz.id,
                        tbl_quiz_attempt.user_id == user.id
                    )
                    attempt_result = await db.execute(attempt_query)
                    attempt = attempt_result.scalars().first()
                    
                    if attempt:
                        if attempt.completed:
                            quiz_data["status"] = "completed"
                        else:
                            quiz_data["status"] = "in_progress"
                    else:
                        quiz_data["status"] = "not_attempted"
                
                quizzes_data.append(quiz_data)
            
            # 페이징 정보 포함한 응답 데이터
            response_data = {
                "total_quizzes": total_quizzes,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_quizzes + page_size - 1) // page_size,
                "quizzes": quizzes_data
            }
            
            return response_data, ErrorType.SUCCESS
            
        except Exception as e:
            print("db get quiz list error:", e)
            return {}, ErrorType.DATABASE_ERROR
            
    async def get_quiz_detail(self, db: AsyncSession, quiz_id: int, page: int, user: tbl_user) -> Tuple[dict, ErrorType]:
        """
        퀴즈 상세 정보를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            quiz_id: 퀴즈 ID
            page: 페이지 번호
            user: 사용자 정보
            
        Returns:
            퀴즈 상세 정보, 오류 타입
        """
        try:
            # 퀴즈 기본 정보 조회
            quiz_query = select(tbl_quiz, tbl_user.username.label("created_by")) \
                .join(tbl_user, tbl_quiz.user_id == tbl_user.id) \
                .where(tbl_quiz.id == quiz_id)
            
            result = await db.execute(quiz_query)
            quiz_row = result.first()
            
            if not quiz_row:
                return None, ErrorType.QUIZ_NOT_FOUND
            
            quiz = quiz_row[0]  # tbl_quiz 객체
            created_by = quiz_row[1]  # username
            
            # 총 문제 수 조회
            question_count_query = select(func.count()).where(tbl_question.quiz_id == quiz_id)
            total_questions = await db.scalar(question_count_query) or 0
            
            # 페이지당 문제 수 계산 (관리자 설정 또는 기본값)
            questions_per_page = min(quiz.selected_questions, 10)  # 기본값: 10개, 최대: selected_questions
            
            # 총 페이지 수 계산
            total_pages = (total_questions + questions_per_page - 1) // questions_per_page
            
            # 문제 목록 조회 (페이징 적용)
            question_query = select(tbl_question) \
                .where(tbl_question.quiz_id == quiz_id) \
                .order_by(tbl_question.id)
            
            # 랜덤 문제 출제 설정이 있는 경우
            if quiz.is_randomized_questions:
                # SQLAlchemy에서 랜덤 정렬 (데이터베이스에 따라 다름)
                question_query = question_query.order_by(func.random())
            
            # 페이징 적용
            question_query = question_query.offset((page - 1) * questions_per_page).limit(questions_per_page)
            
            # 문제 목록 조회
            question_result = await db.execute(question_query)
            questions = question_result.scalars().all()
            
            # 문제 및 선택지 데이터 구성
            questions_data = []
            for question in questions:
                # 선택지 조회
                choice_query = select(tbl_choice).where(tbl_choice.question_id == question.id)
                choice_result = await db.execute(choice_query)
                choices = choice_result.scalars().all()
                
                # 선택지 데이터 구성
                choices_data = []
                for choice in choices:
                    choice_data = {
                        "id": choice.id,
                        "text": choice.content,
                        "is_correct": choice.is_correct
                    }
                    choices_data.append(choice_data)
                
                # 문제 데이터 구성
                question_data = {
                    "id": question.id,
                    "question_text": question.question_text,
                    "choices": choices_data
                }
                questions_data.append(question_data)
            
            # 응답 데이터 구성
            response_data = {
                "quiz_id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "is_randomized_questions": quiz.is_randomized_questions,
                "is_randomized_choices": quiz.is_randomized_choices,
                "selected_questions": quiz.selected_questions,
                "total_questions": total_questions,
                "created_at": quiz.created_at,
                "updated_at": quiz.updated_at,
                "created_by": created_by,
                
                # 페이징 정보
                "current_page": page,
                "total_pages": total_pages,
                "questions_per_page": questions_per_page,
                
                # 문제 목록
                "questions": questions_data
            }
            
            return response_data, ErrorType.SUCCESS
            
        except Exception as e:
            print("db get quiz detail error:", e)
            return None, ErrorType.DATABASE_ERROR
            
    async def start_quiz_session(self, db: AsyncSession, quiz_id: int, user_id: int) -> Tuple[dict, ErrorType]:
        """
        퀴즈 응시 세션을 시작합니다.
        
        Args:
            db: 데이터베이스 세션
            quiz_id: 퀴즈 ID
            user_id: 사용자 ID
            
        Returns:
            세션 정보, 오류 타입
        """
        try:
            # 퀴즈 정보 조회
            quiz_query = select(tbl_quiz).where(tbl_quiz.id == quiz_id)
            quiz_result = await db.execute(quiz_query)
            quiz = quiz_result.scalars().first()
            
            if not quiz:
                return None, ErrorType.QUIZ_NOT_FOUND
            
            # 이미 진행 중인 세션이 있는지 확인
            existing_session_query = select(tbl_quiz_session).where(
                tbl_quiz_session.quiz_id == quiz_id,
                tbl_quiz_session.user_id == user_id,
                tbl_quiz_session.is_completed == False
            )
            existing_session_result = await db.execute(existing_session_query)
            existing_session = existing_session_result.scalars().first()
            
            if existing_session:
                # 기존 세션 정보 반환
                return await self.get_quiz_session(db, existing_session.id, user_id)
            
            # 문제 목록 조회
            question_query = select(tbl_question).where(tbl_question.quiz_id == quiz_id)
            question_result = await db.execute(question_query)
            all_questions = question_result.scalars().all()
            
            if not all_questions:
                return None, ErrorType.QUESTIONS_NOT_FOUND
            
            # 랜덤 문제 선택 (설정된 경우)
            import random
            questions = all_questions.copy()
            if quiz.is_randomized_questions:
                random.shuffle(questions)
            
            # 출제할 문제 수 제한
            if quiz.selected_questions < len(questions):
                questions = questions[:quiz.selected_questions]
            
            # 세션 생성
            session_id = str(uuid.uuid4())
            new_session = tbl_quiz_session(
                id=session_id,
                quiz_id=quiz_id,
                user_id=user_id,
                started_at=datetime.now(),
                is_completed=False
            )
            db.add(new_session)
            await db.flush()
            
            # 문제 세션 생성
            question_sessions = []
            for i, question in enumerate(questions):
                question_session = tbl_question_session(
                    session_id=session_id,
                    question_id=question.id,
                    question_order=i
                )
                db.add(question_session)
                await db.flush()
                question_sessions.append(question_session)
                
                # 선택지 조회
                choice_query = select(tbl_choice).where(tbl_choice.question_id == question.id)
                choice_result = await db.execute(choice_query)
                choices = choice_result.scalars().all()
                
                # 선택지 순서 랜덤화 (설정된 경우)
                if quiz.is_randomized_choices:
                    random.shuffle(choices)
                
                # 선택지 세션 생성
                for j, choice in enumerate(choices):
                    choice_session = tbl_choice_session(
                        question_session_id=question_session.id,
                        choice_id=choice.id,
                        choice_order=j
                    )
                    db.add(choice_session)
            
            await db.commit()
            
            # 생성된 세션 정보 반환
            return await self.get_quiz_session(db, session_id, user_id)
            
        except Exception as e:
            print("db start quiz session error:", e)
            await db.rollback()
            return None, ErrorType.DB_RUN_FAILED
    
    async def get_quiz_session(self, db: AsyncSession, session_id: str, user_id: int) -> Tuple[dict, ErrorType]:
        """
        퀴즈 응시 세션 정보를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            session_id: 세션 ID
            user_id: 사용자 ID
            
        Returns:
            세션 정보, 오류 타입
        """
        try:
            # 세션 정보 조회
            session_query = select(tbl_quiz_session).where(
                tbl_quiz_session.id == session_id,
                tbl_quiz_session.user_id == user_id
            )
            session_result = await db.execute(session_query)
            session = session_result.scalars().first()
            
            if not session:
                return None, ErrorType.SESSION_NOT_FOUND
            
            # 퀴즈 정보 조회
            quiz_query = select(tbl_quiz).where(tbl_quiz.id == session.quiz_id)
            quiz_result = await db.execute(quiz_query)
            quiz = quiz_result.scalars().first()
            
            # 문제 세션 정보 조회
            question_session_query = select(
                tbl_question_session,
                tbl_question.question_text
            ).join(
                tbl_question, tbl_question_session.question_id == tbl_question.id
            ).where(
                tbl_question_session.session_id == session_id
            ).order_by(
                tbl_question_session.question_order
            )
            
            question_session_result = await db.execute(question_session_query)
            question_sessions = question_session_result.all()
            
            # 응답 데이터 구성
            questions_data = []
            for question_session, question_text in question_sessions:
                # 선택지 세션 정보 조회
                choice_session_query = select(
                    tbl_choice_session,
                    tbl_choice.content.label("text"),
                    tbl_choice.id.label("choice_id")
                ).join(
                    tbl_choice, tbl_choice_session.choice_id == tbl_choice.id
                ).where(
                    tbl_choice_session.question_session_id == question_session.id
                ).order_by(
                    tbl_choice_session.choice_order
                )
                
                choice_session_result = await db.execute(choice_session_query)
                choice_sessions = choice_session_result.all()
                
                # 선택지 데이터 구성
                choices_data = []
                for _, choice_text, choice_id in choice_sessions:
                    choice_data = {
                        "choice_id": choice_id,
                        "text": choice_text
                    }
                    choices_data.append(choice_data)
                
                # 문제 데이터 구성
                question_data = {
                    "question_id": question_session.question_id,
                    "question_text": question_text,
                    "choices": choices_data,
                    "selected_choice_id": question_session.selected_choice_id
                }
                questions_data.append(question_data)
            
            # 응답 데이터
            response_data = {
                "quiz_id": quiz.id,
                "session_id": session.id,
                "title": quiz.title,
                "description": quiz.description,
                "questions": questions_data,
                "started_at": session.started_at,
                "is_completed": session.is_completed,
                "completed_at": session.completed_at,
                "score": session.score
            }
            
            return response_data, ErrorType.SUCCESS
            
        except Exception as e:
            print("db get quiz session error:", e)
            return None, ErrorType.DATABASE_ERROR
    
    async def save_answer(self, db: AsyncSession, req: Req_QuizSaveAnswer, user_id: int) -> Tuple[dict, ErrorType]:
        """
        퀴즈 답안을 저장합니다.
        
        Args:
            db: 데이터베이스 세션
            req: 답안 저장 요청
            user_id: 사용자 ID
            
        Returns:
            저장 결과, 오류 타입
        """
        try:
            # 세션 정보 조회
            session_query = select(tbl_quiz_session).where(
                tbl_quiz_session.id == req.session_id,
                tbl_quiz_session.user_id == user_id,
                tbl_quiz_session.is_completed == False  # 완료된 세션은 수정 불가
            )
            session_result = await db.execute(session_query)
            session = session_result.scalars().first()
            
            if not session:
                return None, ErrorType.SESSION_NOT_FOUND
            
            # 문제 세션 정보 조회
            question_session_query = select(tbl_question_session).where(
                tbl_question_session.session_id == req.session_id,
                tbl_question_session.question_id == req.question_id
            )
            question_session_result = await db.execute(question_session_query)
            question_session = question_session_result.scalars().first()
            
            if not question_session:
                return None, ErrorType.QUIZ_SESSION_NOT_FOUND
            
            # 선택지가 해당 문제의 것인지 확인
            choice_query = select(tbl_choice).where(
                tbl_choice.id == req.choice_id,
                tbl_choice.question_id == req.question_id
            )
            choice_result = await db.execute(choice_query)
            choice = choice_result.scalars().first()
            
            if not choice:
                return None, ErrorType.QUIZ_SESSION_NOT_FOUND
            
            # 답안 저장
            question_session.selected_choice_id = req.choice_id
            
            await db.commit()
            
            # 응답 데이터
            response_data = {
                "session_id": req.session_id,
                "question_id": req.question_id,
                "choice_id": req.choice_id
            }
            
            return response_data, ErrorType.SUCCESS
            
        except Exception as e:
            print("db save answer error:", e)
            await db.rollback()
            return None, ErrorType.DB_RUN_FAILED
    
    async def submit_quiz(self, db: AsyncSession, session_id: str, answers: Dict[int, int], user_id: int) -> Tuple[dict, ErrorType]:
        """
        퀴즈 답안을 제출하고 채점합니다.
        
        Args:
            db: 데이터베이스 세션
            session_id: 세션 ID
            answers: 답안 (문제 ID: 선택지 ID)
            user_id: 사용자 ID
            
        Returns:
            채점 결과, 오류 타입
        """
        try:
            # 세션 정보 조회
            session_query = select(tbl_quiz_session).where(
                tbl_quiz_session.id == session_id,
                tbl_quiz_session.user_id == user_id,
                tbl_quiz_session.is_completed == False  # 이미 완료된 세션은 제출 불가
            )
            session_result = await db.execute(session_query)
            session = session_result.scalars().first()

            if not session:
                return None, ErrorType.SESSION_NOT_FOUND

            # 퀴즈 정보 조회
            quiz_query = select(tbl_quiz).where(tbl_quiz.id == session.quiz_id)
            quiz_result = await db.execute(quiz_query)
            quiz = quiz_result.scalars().first()

            # 문제 세션 정보 조회
            question_session_query = select(
                tbl_question_session,
                tbl_question.question_text,
                tbl_question.id.label("question_id")
            ).join(
                tbl_question, tbl_question_session.question_id == tbl_question.id
            ).where(
                tbl_question_session.session_id == session_id
            ).order_by(
                tbl_question_session.question_order
            )

            question_session_result = await db.execute(question_session_query)
            question_sessions = question_session_result.all()

            # 답안 저장 및 채점
            total_questions = len(question_sessions)
            correct_answers = 0
            questions_data = []

            for question_session, question_text, question_id in question_sessions:
                # 요청에서 답안 가져오기
                selected_choice_id = answers.get(question_id)

                # 답안이 있으면 저장
                if selected_choice_id:
                    question_session.selected_choice_id = selected_choice_id

                # 정답 확인
                correct_choice_query = select(tbl_choice).where(
                    tbl_choice.question_id == question_id,
                    tbl_choice.is_correct == True
                )
                correct_choice_result = await db.execute(correct_choice_query)
                correct_choice = correct_choice_result.scalars().first()

                # 선택한 답안 정보
                selected_choice_text = None
                if question_session.selected_choice_id:
                    selected_choice_query = select(tbl_choice).where(
                        tbl_choice.id == question_session.selected_choice_id
                    )
                    selected_choice_result = await db.execute(selected_choice_query)
                    selected_choice = selected_choice_result.scalars().first()
                    if selected_choice:
                        selected_choice_text = selected_choice.content

                # 정답 여부 확인
                is_correct = False
                if question_session.selected_choice_id and correct_choice:
                    is_correct = question_session.selected_choice_id == correct_choice.id
                    question_session.is_correct = is_correct
                    if is_correct:
                        correct_answers += 1

                # 문제 결과 데이터
                question_data = {
                    "question_id": question_id,
                    "question_text": question_text,
                    "selected_choice_id": question_session.selected_choice_id,
                    "selected_choice_text": selected_choice_text,
                    "correct_choice_id": correct_choice.id if correct_choice else None,
                    "correct_choice_text": correct_choice.content if correct_choice else None,
                    "is_correct": is_correct
                }
                questions_data.append(question_data)

            # 점수 계산 (100점 만점)
            score = (correct_answers / total_questions * 100) if total_questions > 0 else 0

            # 세션 완료 처리
            session.is_completed = True
            session.completed_at = datetime.now()
            session.score = score

            await db.commit()

            # 응답 데이터
            response_data = {
                "quiz_id": quiz.id,
                "session_id": session.id,
                "title": quiz.title,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "score": score,
                "started_at": session.started_at,
                "completed_at": session.completed_at,
                "questions": questions_data
            }

            return response_data, ErrorType.SUCCESS

        except Exception as e:
            print("db submit quiz error:", e)
            await db.rollback()
            return None, ErrorType.DATABASE_ERROR