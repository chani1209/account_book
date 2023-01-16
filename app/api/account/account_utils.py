import pymysql
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.classes import Response, AccountData, UpdateAccountData
from module.utils import *

# 메모 추가
async def add_account(email: str, data: AccountData) -> Response:
    try:
        conn = await connect_to_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {
                "email": email,
                "money": data.money,
                "note": data.note,
                "now": convert_kst(),
            }
            sql = "INSERT INTO account VALUES (null, (SELECT email_index FROM user WHERE email = %(email)s), %(now)s, %(now)s, %(money)s, %(note)s, null)"
            cursor.execute(sql, sql_data)
            conn.commit()

    except Exception as e:
        print(e, flush=True)
        return Response(status=False, message="가계부 추가에 실패했습니다.", data=None)

    finally:
        await close_db(conn)

    return Response(status=True, message="가계부 추가에 성공했습니다.", data=None)


# 메모 수정
async def update_account(email: str, data: UpdateAccountData) -> Response:
    try:
        conn = await connect_to_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {
                "email": email,
                "money": data.money,
                "note": data.note,
                "now": convert_kst(),
                "account_index": data.account_index,
            }
            sql = "UPDATE account SET money = %(money)s, note = %(note)s, last_update_time = %(now)s WHERE account_index = %(account_index)s AND email_index = (SELECT email_index FROM user WHERE email = %(email)s)"
            cursor.execute(sql, sql_data)
            conn.commit()

    except Exception as e:
        print(e, flush=True)
        return Response(status=False, message="가계부 수정에 실패했습니다.", data=None)

    finally:
        await close_db(conn)

    return Response(status=True, message="가계부 수정에 성공했습니다.", data=None)


# 메모 삭제
async def delete_account(email: str, account_index: int) -> Response:
    try:
        conn = await connect_to_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {"email": email, "account_index": account_index}
            sql = "SELECT * FROM account WHERE account_index = %(account_index)s AND email_index = (SELECT email_index FROM user WHERE email = %(email)s)"
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result is None:
                return Response(status=False, message="가계부를 찾을 수 없습니다.", data=None)

            # 추후 데이터를 사용할 목적이라면 exposed 컬럼을 생성하여 데이터를 보관하고, 삭제 여부를 확인할 수 있도록 한다.
            sql = "DELETE FROM account WHERE account_index = %(account_index)s AND email_index = (SELECT email_index FROM user WHERE email = %(email)s)"
            cursor.execute(sql, sql_data)
            conn.commit()

    except Exception as e:
        print(e, flush=True)
        return Response(status=False, message="가계부 삭제에 실패했습니다.", data=None)

    finally:
        await close_db(conn)

    return Response(status=True, message="가계부 삭제에 성공했습니다.", data=None)


# 가계부 목록 조회
async def get_account_list(email: str) -> Response:
    try:
        conn = await connect_to_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {"email": email}
            sql = "SELECT * FROM account WHERE email_index = (SELECT email_index FROM user WHERE email = %(email)s)"
            cursor.execute(sql, sql_data)
            result = cursor.fetchall()
            result = json.dumps(result, default=str, ensure_ascii=False)

    except Exception as e:
        print(e, flush=True)

    finally:
        await close_db(conn)
    return Response(status=True, message="가계부 목록 조회에 성공했습니다.", data=result)


# 가계부 상세 조회
async def get_account_detail(email: str, account_index: int) -> Response:
    try:
        conn = await connect_to_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {"email": email, "account_index": account_index}
            sql = "SELECT * FROM account WHERE account_index = %(account_index)s AND email_index = (SELECT email_index FROM user WHERE email = %(email)s)"
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result is None:
                return Response(status=False, message="가계부를 찾을 수 없습니다.", data=None)
            result = json.dumps(result, default=str, ensure_ascii=False)

    except Exception as e:
        print(e, flush=True)

    finally:
        await close_db(conn)
    return Response(status=True, message="가계부 상세 조회에 성공했습니다.", data=result)


# 가계부 세부 내역 복제
async def copy_account_detail(email: str, account_index: int) -> Response:
    try:
        conn = await connect_to_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {
                "email": email,
                "account_index": account_index,
                "now": convert_kst(),
            }
            sql = "SELECT * FROM account WHERE account_index = %(account_index)s AND email_index = (SELECT email_index FROM user WHERE email = %(email)s)"
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()
            if result is None:
                return Response(status=False, message="가계부를 찾을 수 없습니다.", data=None)

            sql_data["money"] = result["money"]
            sql = "INSERT INTO account VALUES (NULL, (SELECT email_index FROM user WHERE email = %(email)s), %(now)s, %(now)s, %(money)s,"
            sql += "null," if result["note"] is None else "%(note)s,"
            if result["note"] is not None:
                sql_data["note"] = result["note"]
            sql += "null," if result["type"] is None else "%(type)s,"
            if result["type"] is not None:
                sql_data["type"] = result["type"]
            sql += "null," if result["url"] is None else "%(url)s,"
            cursor.execute(sql, sql_data)
            conn.commit()

    except Exception as e:
        print(e, flush=True)

    finally:
        await close_db(conn)

    return Response(status=True, message="가계부 세부 내역 복제에 성공했습니다.", data=None)


# 특정 세부내역 공유하는 URL 생성
async def create_account_detail_url(email: str, account_index: int, data) -> Response:
    try:
        conn = await connect_to_db()
        if (
            data.create_time is False
            and data.last_update_time is False
            and data.money is False
            and data.note is False
            and data.type is False
        ):
            return Response(status=False, message="공유할 세부내역이 없습니다.", data=None)
        else:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                url = make_uuid()
                sql_data = {
                    "email": email,
                    "account_index": account_index,
                    "url": url,
                    "now": convert_kst(),
                }
                sql = "INSERT INTO url VALUES (%(account_index)s, "
                sql += "%(url)s,"
                sql += "%(now)s,"
                sql += "null," if not data.create_time else "1,"
                sql += "null," if not data.last_update_time else "1,"
                sql += "null," if not data.money else "1,"
                sql += "null," if not data.note else "1,"
                sql += "null)" if not data.type else "1)"

                cursor.execute(sql, sql_data)
                conn.commit()

    except Exception as e:
        print(e, flush=True)

    finally:
        await close_db(conn)

    return Response(status=True, message="가계부 세부 내역 복제에 성공했습니다.", data=url)


# url로 세부내역 조회
async def get_account_detail_by_url(email: str, url: str) -> Response:
    try:
        conn = await connect_to_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_data = {"email": email, "url": url}
            sql = "SELECT * from account as a INNER JOIN url as u ON a.account_index = u.account_index WHERE a.email_index = (SELECT email_index FROM user WHERE email = %(email)s) AND u.url = %(url)s"
            cursor.execute(sql, sql_data)
            result = cursor.fetchone()

            if result is None:
                return Response(
                    status=False, message="가계부 세부 내역을 찾을 수 없습니다.", data=None
                )

            response_result = dict()
            if result["u.create_time"] == 1:
                response_result["create_time"] = result["create_time"]
            if result["u.last_update_time"] == 1:
                response_result["last_update_time"] = result["last_update_time"]
            if result["u.money"] == 1:
                response_result["money"] = result["money"]
            if result["u.note"] == 1:
                response_result["note"] = result["note"]
            if result["u.type"] == 1:
                response_result["type"] = result["type"]

            response_result = json.dumps(
                response_result, default=str, ensure_ascii=False
            )

    except Exception as e:
        print(e, flush=True)

    finally:
        await close_db(conn)
    return Response(status=True, message="가계부 세부 내역 공유에 성공했습니다.", data=response_result)
