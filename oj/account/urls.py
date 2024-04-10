from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (UserDetailAPI,
                    RegisterUserAPI,
                    LoginAPI,
                    LogoutAPI,
                    UserProfileAPI,
                    EditUserProfileAPI)


urlpatterns = [
    path('register', RegisterUserAPI.as_view(), name='register'),
    path('logout', LogoutAPI.as_view(), name='logout'),
    path('login', LoginAPI.as_view(), name='login'),
    path('profile/<str:username>', UserProfileAPI.as_view(), name='user-profile'),
    path('profile', EditUserProfileAPI.as_view(), name='edit-user-profile'),
    # !test api
    path("user/<int:pk>", UserDetailAPI.as_view()),
    # !used for token test
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
