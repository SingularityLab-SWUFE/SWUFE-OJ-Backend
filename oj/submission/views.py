from .models import Submission, JudgeStatus
from .serializers import SubmissionSerializer, SubmissionDisplaySerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from django.conf import settings

from problem.models import Problem

from utils.token import JWTAuthTokenSerializer
from utils.api import APIView
from utils.judger.client import JudgeServerClient
from utils.judger.config import LANGUAGE_CONFIG


class SubmissionAPI(APIView):

    def get(self, request, pk):
        submission = get_object_or_404(Submission, id=pk)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)


class DebugSubmissionAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        pass


class MakeSubmissionAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        problem_id = request.POST.get('problem_id')

        if not problem_id:
            return self.error('problem_id is required')

        problem = Problem.objects.get(id=problem_id)
        if not problem:
            return self.error('problem not found')

        user = request.user
        # TODO: check if user has permission to submit to this problem

        code = request.POST.get('code')
        if not code:
            return self.error('code cannot be empty')

        language = request.POST.get('language')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
        else:
            ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP

        if not problem.is_remote:
            client = JudgeServerClient(token=settings.JUDGE_SERVER_TOKEN,
                                       server_base_url=f"http://{settings.JUDGE_SERVER_HOST}:{settings.JUDGE_SERVER_PORT}")

            language_config = LANGUAGE_CONFIG.get(language)

            if language == 'C++' or language == 'C':
                time_limit = problem.standard_time_limit
                # JudgeServer uses memory limit in Byte
                memory_limit = problem.standard_memory_limit * 1024 * 1024
            else:
                time_limit = problem.other_time_limit
                memory_limit = problem.other_memory_limit * 1024 * 1024

            data = client.judge(src=code, language_config=language_config,
                                max_cpu_time=time_limit, max_memory=memory_limit,
                                test_case_id=problem.test_case_id, output=True)
            if data['err'] == 'CompileError':
                # TODO: handle compile error
                pass

            test_case_results = data['data']

            status = JudgeStatus.PENDING
            error_info = ""
            for result in test_case_results:
                if result['result'] != JudgeStatus.ACCEPTED:
                    error_info = f'Failed on test {result['test_case']}'
                    status = result['result']
            # if all test cases passed, status is ACCEPTED
            if status == JudgeStatus.PENDING:
                status = JudgeStatus.ACCEPTED
        else:
            # TODO: remote judge
            pass

        submission = Submission.objects.create(
            problem=problem, username=user.username, code=code,
            language=language, result=status, info=test_case_results, ip=ip)
        serializer = SubmissionDisplaySerializer(submission)
        return self.success(serializer.data)
