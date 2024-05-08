from django.urls import path
from .views import RemoteProblemAPI

urlpatterns = [
    path('remote/problem', RemoteProblemAPI.as_view(), name='add_remote_problem')
]
