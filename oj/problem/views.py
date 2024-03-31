import markdown
import re
from .models import Problem, ProblemTag
from .serializers import ProblemSerializer, ProblemListSerializer

from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.shortcuts import render


class ProblemAPI(APIView):

    def get(self, request, pk, *args, **kwargs):
        problem = get_object_or_404(Problem, id=pk)
        serializer = ProblemSerializer(problem)
        return Response(serializer.data)


class ProblemListAPI(APIView):

    def get(self, request):
        problems = Problem.objects.all()
        serializer = ProblemListSerializer(problems, many=True)
        return Response(serializer.data)

class ProblemCreateAPI(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        serializer = ProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProblemUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]  

    def put(self, request, id):
        problem = Problem.objects.get(id=id)
        serializer = ProblemSerializer(problem, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def change_formula(matched):
    formula = matched.group(0)
    formula = formula.replace('_', ' _')
    return '\n<p>'+formula+'</p>\n'


def markdown_format(texts: list[str]):
    for text in texts:
        text = markdown.markdown(re.sub(r'\$\$(.+?)\$\$', change_formula, text),
                                 extension_configs=[
            # 包含 缩写、表格等常用扩展
            'markdown.extensions.extra',
            # 语法高亮扩展
            'markdown.extensions.codehilite',])


def problem_display(request, id):
    problem = Problem.objects.get(id=id)

    markdown_format([problem.description, problem.input, problem.output])

    context = {'problem': problem}
    return render(request, 'problem/detail.html', context)
