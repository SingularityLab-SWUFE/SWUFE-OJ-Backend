from django.urls import path
from .views import SubmissionAPI

urlpatterns = [
    path("submission/<int:pk>", SubmissionAPI.as_view()),
]
