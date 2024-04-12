import jwt
import time

from oj import settings


def get_token_info(token, para='user_id'):
    """
        解析 jwt 得到 payload 里某一字段, 默认为 user_id
    """
    try:
        decode_data = jwt.decode(
            token, secret_key=settings.SECRET_KEY, verify=False, algorithms=['HS256'])
        if int(decode_data['exp']) < int(time.time()):
            return "token expired"
        return decode_data[para]
    except Exception as e:
        return "token error:\n" + str(e)
