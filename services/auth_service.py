
from datetime import timedelta
from fastapi import Depends
from pydantic import with_config
from sqlalchemy import Tuple
from commons.utils.enums import ErrorType
from crud.auth_crud import AuthCRUD, IAuthCRUD
from db.database import DB_SESSION_MNG
from middleware.auth import create_access_token
from models.quiz import tbl_user
from router.v1.auth.protocol import Res_AccountLogin, Res_AccountRegister
from sqlalchemy.ext.asyncio import AsyncSession
from config.config import jwt_config

class AuthService:
    def __init__(
        self,
        auth_crud: IAuthCRUD = Depends(AuthCRUD),
    ):
        self.auth_crud = auth_crud

    async def create_user(self, username: str, password: str, is_admin: bool) -> Res_AccountRegister:
        res = Res_AccountRegister()

        user, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.auth_crud.get_user(s, username))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(ErrorType.USER_NOT_EXISTS)
            return res  

        if user:
            res.result.SetResult(ErrorType.USER_ALREADY_EXISTS)
            return res  
        
        # 새 사용자 생성
        new_user = tbl_user(
            username=username, 
            password=password, 
            is_admin=is_admin
        )
        err = await self.auth_crud.create_user(new_user)
        if err != ErrorType.SUCCESS:
            res.result.SetResult(ErrorType.DB_RUN_FAILED)
            return res
        
        res.username = new_user.username
        res.password = new_user.password
        res.created_at = new_user.created_at

        return res

    async def login(self, username: str, password: str) -> Res_AccountLogin:
        res = Res_AccountLogin()
        user, err_type = await DB_SESSION_MNG.execute_lambda(lambda s: self.auth_crud.get_user(s, username))
        if err_type != ErrorType.SUCCESS:
            res.result.SetResult(ErrorType.USER_NOT_EXISTS)
            return res  
        
        # 사용자 존재여부 확인, 패스워드 체크
        if not user or user.password != password:
            res.result.SetResult(ErrorType.INVALID_PASSWORD)
            return res
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=jwt_config.access_expire_min)
        access_token = create_access_token(
            data={"username": user.username, "id": user.id, "is_admin": user.is_admin},
            expires_delta=access_token_expires
        )

        # refresh_token_expires = timedelta(minutes=jwt_config.refresh_expire_min)
        # refresh_token = create_refresh_token(
        #     data={"username": user.username, "id": user.id, "is_admin": user.is_admin},
        #     expires_delta=refresh_token_expires
        # )
    
        res.access_token = access_token
        res.refresh_token = "refresh_token"
        res.username = user.username
        res.password = user.password

        return res
