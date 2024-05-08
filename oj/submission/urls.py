from django.urls import path
from .views import SubmissionAPI, MakeSubmissionAPI

urlpatterns = [
    path("submission/<int:pk>", SubmissionAPI.as_view()),
    path("submission", MakeSubmissionAPI.as_view(), name='submit'),
]
