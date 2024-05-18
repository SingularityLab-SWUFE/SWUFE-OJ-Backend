from django.http import HttpResponse
from .models import Problem, ProblemTag
from .serializers import ProblemSerializer, ProblemListSerializer, TestCaseUploadForm
from .utils import TestCaseZipProcessor, rand_str

from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from contest.models import Contest
from utils.templates import markdown_format
from utils.token import JWTAuthTokenSerializer
from utils.api import APIView, CSRFExemptAPIView


class ProblemAPI(APIView):

    def get(self, request, problem_id):
        try:
            problem = get_object_or_404(Problem, id=problem_id)
        except Problem.DoesNotExist:
            return self.error(f'Problem with id:{problem_id} does not exist')

        serializer = ProblemSerializer(problem)
        return self.success(serializer.data)


class ProblemListAPI(APIView):

    def get(self, request):

        is_remote = request.query_params.get('is_remote', None)
        source = request.query_params.get('source', None)
        difficulty = request.query_params.get('difficulty', None)
        keyword = request.query_params.get('keyword', None)
        contest_id = request.query_params.get('contest_id', None)

        problems = Problem.objects.all()
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id)
                problems = problems.filter(contest=contest)
            except Contest.DoesNotExist:
                pass
        if is_remote:
            problems = problems.filter(is_remote=True)
        if source:
            problems = problems.filter(source=source)
        if difficulty:
            problems = problems.filter(difficulty=difficulty)
        if keyword:
            problems = problems.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword))
            # or problems = problems.filter(description__icontains=keyword)

        serializer = ProblemListSerializer(problems, many=True)
        return self.success(serializer.data)


class TestCaseAPI(CSRFExemptAPIView, TestCaseZipProcessor):
    
    request_parsers = ()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        problem_id = request.GET.get('problem_id')

        if not problem_id:
            return self.error('problem_id is required')
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return self.error(f'Problem with id:{problem_id} does not exist')
        
        form = TestCaseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # test cases are uploaded as a zip file
            uploaded_zip_file = form.cleaned_data['test_cases']
            spj = form.cleaned_data['spj'] == 'true'
        else:
            return self.error("Test case file upload failed.")
        
        user = request.user

        if not user.is_admin():
            return self.error('一般用户没有权限上传测评样例')
        
        info, test_case_id = self.process_zip(
            uploaded_zip_file, spj=spj)
        
        if problem.test_case_id:
            self.rsync_test_cases(problem.test_case_id, delete=True)
        
        problem.test_case_id = test_case_id
        problem.save()
        
        self.rsync_test_cases(test_case_id)
        
        return self.success({'info': info, 'test_case_id': test_case_id, 'spj': spj})


class ProblemCreateAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        # User object is passed by JWTAuthTokenSerializer
        user = request.user

        if not user.is_admin():
            return self.error('一般用户没有权限创建题目')

        data = {'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'input': request.POST.get('input'),
                'output': request.POST.get('output'),
                'samples': request.POST.get('samples'),
                'standard_time_limit': request.POST.get('standard_time_limit'),
                'standard_memory_limit': request.POST.get('standard_memory_limit'),
                'is_remote': False,
                }

        problem = Problem.objects.create(**data)
        return self.success(ProblemSerializer(problem).data)


def problem_display(request, id):
    problem = Problem.objects.get(id=id)

    markdown_format([problem.description, problem.input, problem.output])

    context = {'problem': problem}
    return render(request, 'problem/detail.html', context)
