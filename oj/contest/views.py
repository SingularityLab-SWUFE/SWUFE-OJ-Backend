from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from utils.api import APIView
from utils.token import JWTAuthTokenSerializer


class ContestViewAPI(APIView):

    def get(self, request, contest_id):
        pass


class ContestAdminAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        pass

    def put(self, request):
        pass
