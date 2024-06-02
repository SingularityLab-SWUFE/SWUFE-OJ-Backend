from .models import Problem, ProblemTag, ProblemSet
from .serializers import (ProblemSerializer, ProblemListSerializer,
                          ProblemSetSerializer, CreateProblemSerializer,
                          TestCaseUploadForm)
from .utils import TestCaseZipProcessor, rand_str

from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from contest.models import Contest
from utils.templates import markdown_format
from utils.token import JWTAuthTokenSerializer
from utils.api import APIView, CSRFExemptAPIView, validate_serializer


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
        problem_set_id = request.query_params.get('problem_set_id', None)
        page = request.query_params.get('page', 1)

        problems = Problem.objects.all()
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id)
                problems = problems.filter(contest=contest)
            except Contest.DoesNotExist:
                pass
        if problem_set_id:
            try:
                problem_set = ProblemSet.objects.get(id=problem_set_id)
                problems = problems.filter(problem_set=problem_set)
            except ProblemSet.DoesNotExist:
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
        paginator = Paginator(problems, 10)
        try:
            problems = paginator.page(page)
        except PageNotAnInteger:
            problems = paginator.page(1)
        except EmptyPage:
            problems = paginator.page(paginator.num_pages)
            
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
        user = request.user

        if not user.is_admin():
            return self.error('一般用户没有权限创建题目')

        data = request.data
        serializer = CreateProblemSerializer(data=data)
        
        if not serializer.is_valid():
            return self.error(serializer.errors)
        
        data = serializer.data
        
        data["is_remote"] = False
        
        if data.get("tags"):
            tags = data.pop('tags')
            for tag in tags:
                try:
                    tag_obj = ProblemTag.objects.get(name=tag)
                except ProblemTag.DoesNotExist:
                    tag_obj = ProblemTag.objects.create(name=tag)
                problem.tags.add(tag_obj)
        
        problem = Problem.objects.create(**data)
        return self.success(ProblemSerializer(problem).data)


class ProblemSetCreateAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]
    
    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description')
        problems = request.data.get('problems')
        problem_set = ProblemSet.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        for problem_id in problems:
            problem = Problem.objects.get(id=problem_id)
            problem_set.problems_included.add(problem)
        return self.success(ProblemSetSerializer(problem_set).data)

    def put(self, request):
        problem_set_id = request.data.get('problem_set_id')
        try:
            problem_set = ProblemSet.objects.get(id=problem_set_id)
        except ProblemSet.DoesNotExist:
            return self.error('Problem set does not exist')
        user = request.user
        if user != problem_set.created_by:
            return self.error('You are not the creator of this problem set')
        
        data = request.data
        
        for k, v in data.items():
            setattr(problem_set, k, v)
        
        problems = request.data.get('problems')
        problem_set.problems_included.clear()
        for problem_id in problems:
            problem = Problem.objects.get(id=problem_id)
            problem_set.problems_included.add(problem)
        
        problem_set.save()
        return self.success(ProblemSetSerializer(problem_set).data)

def problem_display(request, id):
    problem = Problem.objects.get(id=id)

    markdown_format([problem.description, problem.input, problem.output])

    context = {'problem': problem}
    return render(request, 'problem/detail.html', context)
