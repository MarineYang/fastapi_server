
from datetime import timedelta
from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.config import jwt_config

from middleware.auth import create_access_token
from models.quiz import tbl_user
from router.v1.auth.protocol import Res_AccountRegister, Req_AccountCreate, Req_AccountLogin, Res_AccountLogin
from router.v1.validator.dependencies import RemoveNoneResponse
from services.auth_service import AuthService


security = HTTPBearer()
router = APIRouter(
    prefix="/auth",
    tags=["회원가입 및 로그인"],
    responses={404: {"description": "Not found"}}
)

@router.post("/register", response_model=Res_AccountRegister, summary="회원가입",description="회원가입", status_code=status.HTTP_201_CREATED)
async def register(req: Req_AccountCreate, service: AuthService = Depends()):
    return RemoveNoneResponse(await service.create_user(req.username, req.password, req.is_admin))


@router.post("/login", response_model=Res_AccountLogin, summary="로그인",description="로그인", status_code=status.HTTP_201_CREATED)
async def login(req: Req_AccountLogin, service: AuthService = Depends()):
    return RemoveNoneResponse(await service.login(req.username, req.password))


    
    






