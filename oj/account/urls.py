from django.urls import path
from .views import UserDetailAPI, RegisterUserAPIView, LogoutAPIView, UserProfileAPIView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("user/<int:pk>", UserDetailAPI.as_view()),
    path('register', RegisterUserAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('profile/<int:user_id>', UserProfileAPIView.as_view(), name='user-profile'),
    path('login', obtain_auth_token),
]
