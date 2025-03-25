import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from models.quiz import tbl_user
from sqlalchemy.ext.asyncio import AsyncSession
from config.config import jwt_config

# JWT 설정
SECRET_KEY = jwt_config.access_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config.access_expire_min

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        username: str = payload.get("username")
        is_admin: bool = payload.get("is_admin")
        if id is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 인증 정보")
        token_data = {"id": id, "username": username, "is_admin": is_admin}
        return token_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")

# async def get_current_user(token_data: dict = Depends(verify_token), db: AsyncSession = Depends(get_async_db)):
#     user = await db.execute(select(tbl_user).where(tbl_user.id == token_data["id"]))
#     user = user.scalars().first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
#     return user

def get_current_admin_user(current_user: any = Depends(verify_token)) -> tbl_user:
    user = tbl_user(
        id=current_user['id'],
        username=current_user['username'],
        is_admin=current_user['is_admin']
    )
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return user 

def get_current_user(current_user: any = Depends(verify_token)) -> tbl_user:
    user = tbl_user(
        id=current_user['id'],
        username=current_user['username'],
        is_admin=current_user['is_admin']
    )
    return user