import pymysql
import sys
import os
import uuid
import time
import asyncio
from datetime import datetime, timedelta
from jose import JWTError, jwt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.classes import Response

algorithm = "HS256"
secret_key = "payhere"


async def connect_to_db() -> pymysql.connect:
    conn = pymysql.connect(
        host="db",
        user="payhere",
        password="payhere",
        port=3306,
        charset="utf8",
        db="payhere",
    )
    return conn


async def close_db(conn) -> None:
    conn.close()


async def test_db() -> str:
    try:
        conn = await connect_to_db()

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM test"
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result, flush=True)

    except Exception as e:
        print(e)

    finally:
        await close_db(conn)

    return result["message"]


# 액세스 토큰 검증
def verify_token(token: str, token_type: str = "access") -> Response:
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=[algorithm])
        return Response(status=True, message="토큰 검증 성공", data=decoded_token["email"])
    except JWTError:
        return Response(status=False, message="토큰 검증 실패", data=None)


# 시간대 설정
def convert_kst() -> str:
    dt_tm_utc = datetime.strptime(
        time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
    )
    dt_tm_kst = dt_tm_utc + timedelta(hours=9) + timedelta(minutes=5)
    str_date = dt_tm_kst.strftime("%Y-%m-%d %H:%M:%S")
    return str_date


# uuid 생성
def make_uuid(length=8) -> str:
    return str(uuid.uuid4()).replace("-", "")[:length]


# 1분마다 주기적으로 동작
def repeat_every_minute() -> None:
    print("repeat_every_minute", flush=True)
    asyncio.run(delete_db_repeat())


# DB 접속 후 데이터 삭제
async def delete_db_repeat() -> None:
    try:
        conn = await connect_to_db()

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "DELETE FROM url WHERE create_time_url < date_add(NOW(), interval 9 hour)"
            cursor.execute(sql)
            conn.commit()
            print("delete", flush=True)

    except Exception as e:
        print(e)

    finally:
        await close_db(conn)
