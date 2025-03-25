from fastapi import HTTPException
from enum import Enum, auto


class ErrorType(Enum):
    SUCCESS = 0
    FAIL = 1
    USER_NOT_EXISTS = 2
    USER_ALREADY_EXISTS = 3
    INVALID_PASSWORD = 4
    NOT_ADMIN = 5
    QUIZ_NOT_FOUND = 6
    QUIZ_SESSION_NOT_FOUND = 7
    DB_RUN_FAILED = 10
