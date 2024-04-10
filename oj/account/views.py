from django.core.cache import cache
from django.contrib.auth import authenticate
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics

from utils.api import APIView
from utils.token import get_token_info

from .serializers import (JWTAuthTokenSerializer,
                          UserSerializer,
                          RegisterSerializer,
                          UserProfileSerializer,
                          EditUserProfileSerializer)
from .models import User, UserProfile


class UserDetailAPI(APIView):
    def get(self, request, pk, *args, **kwargs):
        user = User.objects.get_object_or_404(id=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class RegisterUserAPI(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LogoutAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def post(self, request):
        '''
            clear the token from cache
        '''
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        user_id = get_token_info(token)
        username = User.objects.get(id=user_id).username
        if cache.has_key(token):
            cache.delete(token)
            return self.success(f"user:{username} has been logged out.")
        else:
            return self.error(f"Token already removed from cache.")


class LoginAPI(APIView):

    def post(self, request):
        data = request.data

        user_exists = User.objects.filter(username=data['username']).exists()
        if not user_exists:
            return self.error("用户不存在")

        user = authenticate(
            request=request, username=data['username'], password=data['password'])
        if user:
            # login(request, user)
            user.last_login = str(timezone.now())
            token = str(user.get_token())
            data = {
                "token": token,
                "user": UserSerializer(user).data
            }
            cache.set(token, user, timeout=60*60*24)
            user.save()
            return self.success(data)
        else:
            return self.error(msg="密码错误")


class UserProfileAPI(APIView):

    def get(self, request, username):
        user_profile = get_object_or_404(UserProfile, user__username=username)
        serializer = UserProfileSerializer(user_profile)
        return self.success(serializer.data)


class EditUserProfileAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthTokenSerializer]

    def put(self, request):
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        user_id = get_token_info(token)
        user_profile = UserProfile.objects.filter(user__id=user_id).first()

        # self.check_object_permissions(request, user_profile)

        serializer = EditUserProfileSerializer(
            user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return self.success(serializer.data)
        return self.error(serializer.errors)
