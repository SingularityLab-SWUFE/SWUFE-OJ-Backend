from .models import Submission, JudgeStatus
from .serializers import SubmissionSerializer, SubmissionDisplaySerializer
from .tasks import judge

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
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        submission = Submission.objects.create(
            problem=problem, username=user.username, code=code,
            language=language, result=JudgeStatus.PENDING, ip=ip)
        
        if not problem.is_remote:
            # background task for judge
            judge.send(submission.id, int(problem_id))
        else:
            # TODO: remote judge
            pass

        serializer = SubmissionDisplaySerializer(submission)
        return self.success(serializer.data)
