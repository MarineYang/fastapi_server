CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- tbl_user 테이블 생성
CREATE TABLE tbl_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- tbl_quiz 테이블 생성
CREATE TABLE tbl_quiz (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    selected_questions INTEGER DEFAULT 10,
    is_randomized_questions BOOLEAN DEFAULT FALSE,
    is_randomized_choices BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES tbl_user (id)
);

-- tbl_question 테이블 생성
CREATE TABLE tbl_question (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (quiz_id) REFERENCES tbl_quiz (id)
);

-- tbl_choice 테이블 생성
CREATE TABLE tbl_choice (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (question_id) REFERENCES tbl_question (id)
);

-- tbl_quiz_attempt 테이블 생성
CREATE TABLE tbl_quiz_attempt (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (quiz_id) REFERENCES tbl_quiz (id),
    FOREIGN KEY (user_id) REFERENCES tbl_user (id)
);

-- tbl_user_answer 테이블 생성
CREATE TABLE tbl_user_answer (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    choice_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (attempt_id) REFERENCES tbl_quiz_attempt (id),
    FOREIGN KEY (question_id) REFERENCES tbl_question (id),
    FOREIGN KEY (choice_id) REFERENCES tbl_choice (id)
);

-- tbl_quiz_session 테이블 생성
CREATE TABLE tbl_quiz_session (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    score FLOAT,
    FOREIGN KEY (quiz_id) REFERENCES tbl_quiz (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES tbl_user (id) ON DELETE CASCADE
);

-- tbl_question_session 테이블 생성
CREATE TABLE tbl_question_session (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    question_id INTEGER NOT NULL,
    question_order INTEGER NOT NULL,
    selected_choice_id INTEGER,
    is_correct BOOLEAN,
    FOREIGN KEY (session_id) REFERENCES tbl_quiz_session (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES tbl_question (id) ON DELETE CASCADE,
    FOREIGN KEY (selected_choice_id) REFERENCES tbl_choice (id) ON DELETE SET NULL
);

-- tbl_choice_session 테이블 생성
CREATE TABLE tbl_choice_session (
    id SERIAL PRIMARY KEY,
    question_session_id INTEGER NOT NULL,
    choice_id INTEGER NOT NULL,
    choice_order INTEGER NOT NULL,
    FOREIGN KEY (question_session_id) REFERENCES tbl_question_session (id) ON DELETE CASCADE,
    FOREIGN KEY (choice_id) REFERENCES tbl_choice (id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX idx_quiz_user_id ON tbl_quiz(user_id);
CREATE INDEX idx_question_quiz_id ON tbl_question(quiz_id);
CREATE INDEX idx_choice_question_id ON tbl_choice(question_id);
CREATE INDEX idx_quiz_attempt_quiz_id ON tbl_quiz_attempt(quiz_id);
CREATE INDEX idx_quiz_attempt_user_id ON tbl_quiz_attempt(user_id);
CREATE INDEX idx_user_answer_attempt_id ON tbl_user_answer(attempt_id);
CREATE INDEX idx_user_answer_question_id ON tbl_user_answer(question_id);
CREATE INDEX idx_quiz_session_quiz_id ON tbl_quiz_session(quiz_id);
CREATE INDEX idx_quiz_session_user_id ON tbl_quiz_session(user_id);
CREATE INDEX idx_question_session_session_id ON tbl_question_session(session_id);
CREATE INDEX idx_question_session_question_id ON tbl_question_session(question_id);
CREATE INDEX idx_choice_session_question_session_id ON tbl_choice_session(question_session_id);
CREATE INDEX idx_choice_session_choice_id ON tbl_choice_session(choice_id);