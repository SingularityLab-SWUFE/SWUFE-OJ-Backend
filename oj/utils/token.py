import jwt
import time
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (InvalidToken,
                                                 AuthenticationFailed)

from django.conf import settings
from account.models import User


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


class JWTAuthTokenSerializer(JWTAuthentication):

    def get_user(self, token):
        try:
            user_id = get_token_info(str(token))
        except KeyError:
            raise InvalidToken('Invalid token')

        try:
            user = User.objects.get(**{'id': user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='404')

        return user
