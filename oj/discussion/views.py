from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from utils.api import APIView
from utils.token import JWTAuthTokenSerializer


class PostViewAPI(APIView):

    def get(self, request, id):
        pass


class PostUserAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JWTAuthTokenSerializer

    def post(self, request):
        pass

    def put(self, request):
        pass

    def delete(self, request):
        pass


class CommentViewAPI(APIView):
    '''
        Given post_id, return all comments of the post.
    '''

    def get(self, request):
        pass


class CommentUserAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JWTAuthTokenSerializer

    def post(self, request):
        pass
