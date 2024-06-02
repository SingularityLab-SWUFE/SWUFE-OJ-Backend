from django.urls import path
from .views import (ProblemAPI, ProblemListAPI, ProblemCreateAPI, TestCaseAPI,
                    ProblemSetCreateAPI,
                    problem_display)

urlpatterns = [
    path("problem/<int:problem_id>", ProblemAPI.as_view(), name='get_problem'),
    path("problem/", ProblemListAPI.as_view(), name='get_problem_list'),
    path("problem", ProblemCreateAPI.as_view(), name='create_problem'),
    path("problem/testcase", TestCaseAPI.as_view(), name='create_testcase'),
    path("problem/list/admin", ProblemSetCreateAPI.as_view(), name='create_problem_set'),
    # problem template page
    path('problem/display/<int:id>', problem_display, name='problem_display'),
]
