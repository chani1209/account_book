#---------------------------------------------------------
# 외부 모듈
from fastapi import APIRouter, Depends, HTTPException, Header, File, Form, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import os
import sys
#---------------------------------------------------------
# 내부 모듈
from .account_utils import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from module.utils import *
from model.classes import *
#---------------------------------------------------------

router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}},
)

# '오늘' 사용한 돈의 금액과 관련된 메모 작성
@router.post("/today")
async def account_today_create(data: AccountData, access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await add_account(response_token.data, data)

    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message})
    else:
        raise HTTPException(status_code=400, detail=response.message)


# 수정을 원하는 내역은 금액과 메모를 수정 가능
@router.put("/today")
async def account_today_update(data: UpdateAccountData, access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await update_account(response_token.data, data)

    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 가계부에서 원하는 내역은 삭제 가능
@router.delete("/today/{account_index}")
async def account_today_delete(account_index: int, access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await delete_account(response_token.data, account_index)

    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 가계부에서 이제까지 기록한 가계부 리스트 확인 가능
@router.get("/list")
async def account_list(access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await get_account_list(response_token.data)
    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message, 'data': response.data})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 가계부에서 특정 세부내역 확인 가능
@router.get("/account_detail/{account_index}")
async def account_detail(account_index: int, access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await get_account_detail(response_token.data, account_index)
    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message, 'data': response.data})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 가계부의 세부 내역 복제 가능
@router.get('/account_copy/{account_index}')
async def account_copy(account_index: int, access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await copy_account_detail(response_token.data, account_index)
    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message, 'data': response.data})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 가계부의 특정 세부내역 공유하는 URL 생성 -> 특정 시간 후 만료
@router.post('/account_share/{account_index}')
async def account_share(account_index: int,data:UrlDetail, access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await create_account_detail_url(response_token.data, account_index, data)
    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message, 'data': response.data})
    else:
        raise HTTPException(status_code=400, detail=response.message)

# 단축 url로 접근하여 가계부 세부내역 확인 가능
@router.get('/account_share/{short_url}')
async def account_share(short_url: str, access_token: str = Header(None)):
    if not access_token:
        raise HTTPException(status_code=400, detail='Invalid access token')
    response_token = verify_token(access_token, 'access')

    if not response_token.status:
        raise HTTPException(status_code=401, detail='Invalid access token')
    
    response = await get_account_detail_by_url(response_token.data, short_url)
    if response.status:
        return JSONResponse(status_code=200, content={'message': response.message, 'data': response.data})
    else:
        raise HTTPException(status_code=400, detail=response.message)