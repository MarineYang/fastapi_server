from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid
from datetime import datetime


CONTENTS_BASE = declarative_base()

class tbl_user(CONTENTS_BASE):
    __tablename__ = "tbl_user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
    
    # 관계 정의
    quizzes = relationship("tbl_quiz", back_populates="user")
    quiz_attempts = relationship("tbl_quiz_attempt", back_populates="user")
    quiz_sessions = relationship("tbl_quiz_session", back_populates="user")


class tbl_quiz(CONTENTS_BASE):
    __tablename__ = "tbl_quiz"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    questions = relationship("tbl_question", back_populates="quiz", cascade="all, delete-orphan")
    user_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    selected_questions = Column(Integer, default=10)  # 출제할 문제 수
    is_randomized_questions = Column(Boolean, default=False)  # 문제 랜덤 배치 여부
    is_randomized_choices = Column(Boolean, default=False)  # 선택지 랜덤 배치 여부
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 정의
    user = relationship("tbl_user", back_populates="quizzes")
    attempts = relationship("tbl_quiz_attempt", back_populates="quiz", cascade="all, delete-orphan")
    sessions = relationship("tbl_quiz_session", back_populates="quiz")
    
class tbl_question(CONTENTS_BASE):
    __tablename__ = "tbl_question"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("tbl_quiz.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    quiz = relationship("tbl_quiz", back_populates="questions")
    choices = relationship("tbl_choice", back_populates="question", cascade="all, delete-orphan")


class tbl_choice(CONTENTS_BASE):
    __tablename__ = "tbl_choice"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("tbl_question.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    question = relationship("tbl_question", back_populates="choices") 

class tbl_quiz_attempt(CONTENTS_BASE):
    __tablename__ = "tbl_quiz_attempt"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("tbl_quiz.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    score = Column(Integer, default=0)  # 점수
    completed = Column(Boolean, default=False)  # 완료 여부
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    quiz = relationship("tbl_quiz", back_populates="attempts")
    user = relationship("tbl_user", back_populates="quiz_attempts")
    answers = relationship("tbl_user_answer", back_populates="attempt", cascade="all, delete-orphan")

class tbl_user_answer(CONTENTS_BASE):
    __tablename__ = "tbl_user_answer"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("tbl_quiz_attempt.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("tbl_question.id"), nullable=False)
    choice_id = Column(Integer, ForeignKey("tbl_choice.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    attempt = relationship("tbl_quiz_attempt", back_populates="answers")
    question = relationship("tbl_question")
    choice = relationship("tbl_choice")

# 퀴즈 응시 세션 테이블
class tbl_quiz_session(CONTENTS_BASE):
    __tablename__ = "tbl_quiz_session"
    
    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(Integer, ForeignKey("tbl_quiz.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=True)
    
    # 관계 설정
    quiz = relationship("tbl_quiz", back_populates="sessions")
    user = relationship("tbl_user", back_populates="quiz_sessions")
    # 명시적으로 primaryjoin 조건 지정
    question_sessions = relationship(
        "tbl_question_session", 
        back_populates="quiz_session", 
        primaryjoin="tbl_quiz_session.id == tbl_question_session.session_id",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<QuizSession(id={self.id}, quiz_id={self.quiz_id}, user_id={self.user_id})>"

# 문제 세션 테이블 (퀴즈 응시 시 출제된 문제)
class tbl_question_session(CONTENTS_BASE):
    __tablename__ = "tbl_question_session"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey("tbl_quiz_session.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("tbl_question.id", ondelete="CASCADE"), nullable=False)
    question_order = Column(Integer, nullable=False)
    selected_choice_id = Column(Integer, ForeignKey("tbl_choice.id", ondelete="SET NULL"), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    
    # 관계 설정 - back_populates 속성 확인
    quiz_session = relationship(
        "tbl_quiz_session", 
        back_populates="question_sessions",
        primaryjoin="tbl_question_session.session_id == tbl_quiz_session.id"
    )
    question = relationship("tbl_question")
    selected_choice = relationship("tbl_choice", foreign_keys=[selected_choice_id])
    # 명시적으로 primaryjoin 조건 지정
    choice_sessions = relationship(
        "tbl_choice_session", 
        back_populates="question_session", 
        primaryjoin="tbl_question_session.id == tbl_choice_session.question_session_id",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<QuestionSession(id={self.id}, session_id={self.session_id}, question_id={self.question_id})>"

# 선택지 세션 테이블 (퀴즈 응시 시 출제된 선택지)
class tbl_choice_session(CONTENTS_BASE):
    __tablename__ = "tbl_choice_session"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_session_id = Column(Integer, ForeignKey("tbl_question_session.id", ondelete="CASCADE"), nullable=False)
    choice_id = Column(Integer, ForeignKey("tbl_choice.id", ondelete="CASCADE"), nullable=False)
    choice_order = Column(Integer, nullable=False)
    
    # 관계 설정 - back_populates 속성 확인
    question_session = relationship(
        "tbl_question_session", 
        back_populates="choice_sessions",
        primaryjoin="tbl_choice_session.question_session_id == tbl_question_session.id"
    )
    choice = relationship("tbl_choice")
    
    def __repr__(self):
        return f"<ChoiceSession(id={self.id}, question_session_id={self.question_session_id}, choice_id={self.choice_id})>"