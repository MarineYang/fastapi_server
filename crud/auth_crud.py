from sqlalchemy import select
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from commons.utils.enums import ErrorType
from models.quiz import tbl_user
from abc import ABC, abstractmethod


class IAuthCRUD(ABC):

    @abstractmethod
    async def create_user(self, db: AsyncSession, username: str) -> Tuple[tbl_user, ErrorType]:
        pass

    @abstractmethod
    async def get_user(self, db: AsyncSession, username: str) -> Tuple[tbl_user, ErrorType]:
        pass

    @abstractmethod
    async def update_user(self, db: AsyncSession, username: str) -> ErrorType:
        pass    
    

class AuthCRUD(IAuthCRUD):
    async def create_user(self, db: AsyncSession, user: tbl_user) -> ErrorType:
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return ErrorType.SUCCESS
        except Exception as e:
            print("db create user error :", e)
            await db.rollback()
            return ErrorType.DB_RUN_FAILED

    async def get_user(self, db: AsyncSession, username: str) -> Tuple[tbl_user, ErrorType]:
        try:
            result = await db.execute(
                select(tbl_user).where(tbl_user.username == username)
            )
            existing_user = result.scalars().first()
            return existing_user, ErrorType.SUCCESS
        except Exception as e:
            print("db get user error :", e)
            return None, ErrorType.DB_RUN_FAILED

    async def update_user(self, username: str) -> ErrorType:
        pass    

