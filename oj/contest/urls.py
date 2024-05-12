from django.urls import path
from .views import ContestAdminAPI, ContestViewAPI

urlpatterns = [
    path('/contest/<int:contest_id>/', ContestViewAPI.as_view(), name='contest_view_api'),
    path('/contest/', ContestAdminAPI.as_view(), name='contest_admin_api'),
]
