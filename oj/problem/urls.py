from django.urls import path
from .views import ProblemAPI, problem_display

urlpatterns = [
    path("problems/<int:pk>", ProblemAPI.as_view()),
    path('problems/display/<int:id>', problem_display, name='problem_display'),
]
