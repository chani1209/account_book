import re
import os
import sys
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from module.utils import *
from model.classes import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 회원가입
async def sign_up(data) -> Response:
    # 이메일 형식 검사
    if not email_validation(data.email):
        return Response(status=False, message="이메일 형식이 올바르지 않습니다.", data=None)

    # 이메일 중복 검사
    if not await email_duplicate_check(data.email):
        return Response(status=False, message="이미 존재하는 이메일입니다.", data=None)

    if not await sign_up_db(data.email, data.password):
        return Response(status=False, message="회원가입에 실패했습니다.", data=None)

    return Response(status=True, message="회원가입에 성공했습니다.", data=None)


# 이메일 형식 검사
def email_validation(email: str):
    email_regex = re.compile(r"[a-z0-9]+@[a-z]+\.[a-z]{2,3}")
    return email_regex.match(email)


# 이메일 중복 검사
async def email_duplicate_check(email: str):
    try:
        conn = await connect_to_db()

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {"email": email}
            sql = "SELECT * FROM user WHERE email = %(email)s"
            cursor.execute(sql, sql_data)
            result = cursor.fetchall()
            if result:
                return False

    except Exception as e:
        print(e, flush=True)

    finally:
        await close_db(conn)

    return True


# 비밀번호 해시
def get_password_hash(password: str):
    return pwd_context.hash(password)


# 회원가입
async def sign_up_db(email: str, password: str):
    try:
        conn = await connect_to_db()

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {"email": email, "password": get_password_hash(password)}
            sql = "INSERT INTO user VALUES (null, %(email)s, %(password)s)"
            cursor.execute(sql, sql_data)
            conn.commit()

    except Exception as e:
        print(e, flush=True)
        return False

    finally:
        await close_db(conn)


# 로그인
async def login(data) -> Response:
    password = data.password.encode("utf-8")

    try:
        conn = await connect_to_db()

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {"email": data.username}
            sql = "SELECT * FROM user WHERE email = %(email)s"
            cursor.execute(sql, sql_data)
            user_data = cursor.fetchone()

            if not user_data:
                return Response(status=False, message="존재하지 않는 이메일입니다.", data=None)

            if not verify_password(password, user_data["password"]):
                return Response(status=False, message="비밀번호가 일치하지 않습니다.", data=None)

            access_token = create_token(data.username)
            refresh_token = create_token(data.username, timedelta(days=1))

    except Exception as e:
        print(e, flush=True)
        return Response(status=False, message="로그인에 실패했습니다.", data=None)

    finally:
        await close_db(conn)

    return Response(
        status=True, message="로그인에 성공했습니다.", data=[access_token, refresh_token]
    )


# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# 액세스 토큰 생성(유효기간 1시간, 담겨있는 정보 이메일)
def create_token(email: str, expires_delta: timedelta = None):
    data = {"email": email}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, secret_key, algorithm=algorithm)
    return encoded_jwt
