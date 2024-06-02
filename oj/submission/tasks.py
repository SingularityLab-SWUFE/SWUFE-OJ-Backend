import dramatiq

from .models import Submission
from utils.judger.dispatcher import JudgerDispatcher


@dramatiq.actor
def judge(submission_id, problem_id):
    JudgerDispatcher(submission_id, problem_id).judge()
