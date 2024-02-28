from django.urls import path
from .views import RemoteSubmissionAPI

urlpatterns = [
    path("remote/submission", RemoteSubmissionAPI.as_view()),
]
