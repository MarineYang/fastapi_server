from asyncio import current_task
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util._collections import immutabledict
from commons.utils.enums import ErrorType
from commons.utils.singleton import Singleton
from config.config import db_config

class DBSessionManager(Singleton):
    def __init__(self):
        if not DBSessionManager.is_init():
            DBSessionManager.set_init()
            self.__DB_URL = f"postgresql+asyncpg://{db_config.db_username}:{db_config.db_password}@{db_config.db_host}:{db_config.db_port}/{db_config.db_name}"
            self.__ENGINE = create_async_engine(
                self.__DB_URL, 
                pool_size=50, max_overflow=100, pool_pre_ping=True, pool_recycle=600
            )

            self.__SCOPED_SESSION = async_scoped_session(sessionmaker(self.__ENGINE, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False), scopefunc=current_task)
        else:
            print("already init DBSessionManager")

    async def start_session(self) -> AsyncSession:
        return self.__SCOPED_SESSION()
    
    async def end_session(self):
        await self.__SCOPED_SESSION.remove()
    
    async def execute_lambda(self, func):
        """
        One query called
        """
        s = await self.start_session()
        try:
            return await func(s)
        finally:
            await self.end_session()

    async def add(self, db: AsyncSession, query, err_msg="DB Operation Failed", raise_error=True, callback: callable = None) -> ErrorType:
        try:
            if hasattr(query, "column_descriptions"):
                raise RuntimeError("DO NOT USE SELECT QUERY IN DBJOB")
            res = await db.execute(query, execution_options=immutabledict({"synchronize_session": "fetch"}))

            if callback is not None:
                callbackRes = callback(res)
                if callbackRes is not None:
                    return callbackRes

            return ErrorType.SUCCESS

        except Exception as ex:
            await db.rollback()
            err_type = ErrorType.DB_RUN_FAILED
            print(f"[{err_type.name}] {err_msg=}, {ex=}")
            if raise_error:
                raise RuntimeError(err_type.name, err_msg)
            else:
                return err_type
            

    async def execute(self, db: AsyncSession, query, err_msg="DB Query Execution Failed", raise_error=True) -> tuple[ErrorType, list]:
        try:
            if not hasattr(query, "column_descriptions"):
                raise RuntimeError("DO NOT USE NON-SELECT QUERY IN DBJOB")
            res = await db.execute(query, execution_options=immutabledict({"synchronize_session": "fetch"}))

            return ErrorType.SUCCESS, res.scalars().fetchall() if 1 == len(query.column_descriptions) else res.all()
        except Exception as ex:
            err_type = ErrorType.DB_RUN_FAILED
            print(f"[{err_type.name}] {err_msg=}, {ex=}")

            if raise_error:
                raise RuntimeError(err_type.name, err_msg)
            else:
                return err_type, []

DB_SESSION_MNG = DBSessionManager()

    

