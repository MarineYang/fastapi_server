import asyncio
import os
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.gzip import GZipMiddleware
from typing import Any
from config.config import web_server_config
from commons.utils.gtime import GTime
import router.v1.auth
import router.v1.auth.auth
import router.v1.quiz.quiz


form = GTime.UTC().strftime("%Y-%m-%d %H:%M:%S")
API_SERVER_START_TIME = form


# router description
# https://scshim.tistory.com/575
app = FastAPI(title="Project Quiz System Api Server")

# require client reqeust add header 'Accept-Encoding: gzip'
# body 1000 bytes upper gzip compressed
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get(path="/healthz", responses={404: {"description": "Not found"}})
async def healthz():
    return API_SERVER_START_TIME



# 퀴즈 라우터 등록
app.include_router(router.v1.quiz.quiz.router, prefix="/v1")
# 인증 라우터 등록
app.include_router(router.v1.auth.auth.router, prefix="/v1")