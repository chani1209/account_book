from pydantic import BaseModel, Field, BaseSettings
from typing import List, Any, Union
from typing import Union


class LoginData(BaseModel):
    email: str = Field(..., example="payhere@payhere.com")
    password: str = Field(..., example="payhere")


class AccountData(BaseModel):
    money: int = Field(..., example=10000)
    note: str = Field(..., example="")


class UpdateAccountData(AccountData):
    account_index: int = Field(..., example=1)


class UrlDetail(BaseModel):
    create_time: bool = None
    last_update_time: bool = None
    money: bool = None
    note: bool = None
    type: bool = None


class Response(BaseModel):
    status: bool = Field(..., example="success")
    message: str = Field(..., example="Payment was successful")
    data: Union[List[Any], Any] = Field(..., example="")
