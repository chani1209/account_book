#---------------------------------------------------------
# 외부 모듈
from fastapi import FastAPI, Request, File, UploadFile, Form, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
#---------------------------------------------------------
# 내부 모듈
from module.utils import *
from api.auth import auth
from api.account import account
#---------------------------------------------------------
# FastAPI 설정
description = """
## FASTAPI 를 이용한 MAIN API

### API 목록
- auth
- account_book
"""

app = FastAPI(
    description=description,
    )

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(account.router, prefix='', tags=['test'])
app.include_router(auth.router, prefix='', tags=['test'])

# 정해진 시간마다 실행
from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')
sched.add_job(repeat_every_five_minute, 'interval', minutes=5)
sched.start()


# ---------------------------------------------------------
# 파비콘
@app.get('/favicon.ico')
def favicon():
    return FileResponse('static/favicon.ico')

# 개통 테스트
@app.get("/")
async def root():
    message = await test_db()
    return JSONResponse(status_code=200, content={'message': message})