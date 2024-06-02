from django.urls import path
from .views import ContestAdminAPI, ContestViewAPI, ContestRegisterAPI, ContestRankAPI

urlpatterns = [
    path('contest/', ContestViewAPI.as_view(), name='contest_view_api'),
    path('contest/admin', ContestAdminAPI.as_view(), name='contest_admin_api'),
    path('contest/register', ContestRegisterAPI.as_view(), name='contest_register_api'),
    path('contest/rank', ContestRankAPI.as_view(), name='contest_rank_api')
]
