from django.urls import path
from .views import UserDetailAPI, RegisterUserAPIView, LogoutAPIView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("get-details", UserDetailAPI.as_view()),
    path('register', RegisterUserAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('login', obtain_auth_token),
]
