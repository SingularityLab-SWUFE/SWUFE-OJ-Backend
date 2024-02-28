from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from problem.models import Problem, ProblemTag
from submission.models import Submission
from remote.request_sender import submit, user_login, get_submission_status
import requests
import re


class LoginFailedError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# Create your views here.


class RemoteSubmissionAPI(APIView):
    def get(self, request):
        source = request.GET.get('source')
        rid = request.GET.get('rid')

        if source == "HDU":
            info = get_submission_status(rid)
        elif source == "CF":
            pass
        return Response(info)

    def post(self, request):
        # 接受一个用户id, 作为request参数, 如果没有绑定, 采用共有账号
        user_id = request.GET.get('user_id')
        # 利用绑定账号提交
        # if user.is_bond
        if user_id:
            # TODO
            pass
        else:
            login_resp = user_login(
                settings.HDU_ACCOUNT, settings.HDU_PASSWORD)

            if login_resp.status_code != 302:
                raise LoginFailedError(f'Login failed. Status code {\
                                       login_resp.status_code}')
            cookies = login_resp.cookies
            pid = request.POST.get('pid')
            try:
                problem = Problem.objects.get(remote_id=pid, source="HDU")
            except Problem.DoesNotExist:
                return self.error('Problem does not exist')
            code = request.POST.get('code')
            lang = request.POST.get('lang')

            submit_resp = submit(code, pid, lang, cookies)
            # 找到远程本次 submission 的 id
            matches = re.findall(
                r'<td height=22px>(\d+)<\/td>', submit_resp.text)
            rid = matches[0]
            return Response(get_submission_status(rid))


class RemoteProblemInfoAPI(APIView):
    def get(self, request):
        pass
