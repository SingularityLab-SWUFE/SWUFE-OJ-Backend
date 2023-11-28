from .serializers import UserSerializer, RegisterSerializer, \
    UserProfileSerializer, EditUserProfileSerializer
from .models import UserProfile
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics


class UserDetailAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, pk, *args, **kwargs):
        user = User.objects.get_object_or_404(id=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LogoutAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({"message": "User logged out successfully."})


class UserProfileAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, user_id, *args, **kwargs):
        user_profile = UserProfile.objects.filter(user__id=user_id).first()
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def put(self, request, user_id, *args, **kwargs):
        user_profile = UserProfile.objects.filter(user__id=user_id).first()

        self.check_object_permissions(request, user_profile)

        serializer = EditUserProfileSerializer(
            user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
