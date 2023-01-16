#---------------------------------------------------------
# 외부 모듈
from fastapi import APIRouter, Depends, HTTPException, Header, File, Form, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, FileResponse
import os.path
#---------------------------------------------------------
# 내부 모듈
from .auth_utils import *
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.classes import *
#---------------------------------------------------------

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

# 기능 추가

# 회원가입
@router.post('/signup')
async def auth_create_user(data: LoginData):
    response = await sign_up(data)
    if response.status:
       return JSONResponse(status_code=200, content={'message': 'success'})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 로그인
@router.post('/login')
async def auth_login(data: OAuth2PasswordRequestForm = Depends()):
    response = await login(data)
    if response.status:
        return JSONResponse(status_code=200, content={'message': 'success', 'access_token': response.data[0], 'refresh_token': response.data[1]})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 리프레시 토큰으로 엑세스 토큰 재발급
@router.post('/refresh')
async def auth_refresh_token(refresh_token: str = Header(...)):
    response = verify_token(refresh_token, 'refresh')
    if response.status:
        access_token = create_token(response.data)
        refersh_token = create_token(response.data, timedelta(days=1))
        return JSONResponse(status_code=200, content={'message': 'success', 'access_token': access_token, 'refresh_token': refersh_token})
    else:
        raise HTTPException(status_code=400, detail='Invalid refresh token')


# 토큰 확인

# auth2 인증
