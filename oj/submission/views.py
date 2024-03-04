from .models import Submission
from .serializers import SubmissionSerializer

from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.shortcuts import render


class SubmissionAPI(APIView):

    def get(self, request, pk, *args, **kwargs):
        submission = get_object_or_404(Submission, id=pk)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)
