from datetime import datetime
from pydantic import BaseModel, Field

from commons.models.gmodel import WebPacketProtocol, Res_WebPacketProtocol

class AuthProtocol(WebPacketProtocol):
    pass

class Req_AccountLogin(AuthProtocol):
    username: str = Field(..., description="사용자 이름", example="test")
    password: str = Field(..., description="사용자 비밀번호", example="test")


class Res_AccountLogin(Res_WebPacketProtocol):
    username: str = ""
    password: str = ""
    access_token: str = ""
    refresh_token: str = ""

class Req_AccountCreate(AuthProtocol):
    username: str = Field(..., description="사용자 이름", example="test")
    password: str = Field(..., description="사용자 비밀번호", example="test")
    is_admin: bool = Field(..., description="사용자 역할 (user 또는 admin)")



class Res_AccountRegister(Res_WebPacketProtocol):
    username: str = ""
    password: str = ""
    created_at: datetime

# class Account(AccountBase):
#     id: int
