from submission.models import Submission, JudgeStatus
from problem.models import Problem
from django.conf import settings

from .client import JudgeServerClient, JudgeServerClientError
from .config import LANGUAGE_CONFIG

import logging

logger = logging.getLogger(__name__)


class JudgerDispatcher:
    '''
        Dispatch the submission to the judge servers and return the result.
    '''

    def __init__(self, submission_id, problem_id):
        self.submission = Submission.objects.get(id=submission_id)
        self.contest_id = self.submission.contest_id

        if self.contest_id:
            self.problem = Problem.objects.select_related('contest').get(
                id=problem_id, contest__id=self.contest_id)
            self.contest = self.problem.contest
        else:
            self.problem = Problem.objects.get(id=problem_id)

        self.client = JudgeServerClient(
            token=settings.JUDGE_SERVER_TOKEN,
            server_base_url=f"http://{settings.JUDGE_SERVER_HOST}:{settings.JUDGE_SERVER_PORT}")

    def judge(self):
        code = self.submission.code
        language = self.submission.language
        language_config = LANGUAGE_CONFIG.get(language)

        # TODO: spj

        judge_data = {
            "src": code,
            "language_config": language_config,
            "test_case_id": self.problem.test_case_id,
        }

        if language == 'C' or language == 'C++':
            judge_data['max_cpu_time'] = self.problem.standard_time_limit
            judge_data['max_memory'] = self.problem.standard_memory_limit * 1024 * 1024
        else:
            judge_data['max_cpu_time'] = self.problem.other_time_limit
            judge_data['max_memory'] = self.problem.other_memory_limit * 1024 * 1024

        Submission.objects.filter(id=self.submission.id).update(
            result=JudgeStatus.JUDGING)
        
        logger.info('Sending judge request to judge server...')
        # JSON response from judge server
        resp = self.client.judge(**judge_data)
        
        # for debug
        # logger.info(f'Judge server sent with response: {resp}')
        
        if not resp or resp["err"] == "JudgeClientError":
            self.submission.result = JudgeStatus.SYSTEM_ERROR
            return

        if resp["err"] == "Compile Error":
            # TODO: handle compile error
            pass

        data: list[dict] = resp["data"]

        data.sort(key=lambda x: int(x["test_case"]))
        self.submission.info = data

        self._get_statistic_info(data)

        error_test_cases = [
            case for case in data if case['result'] != JudgeStatus.ACCEPTED]

        if not error_test_cases:
            self.submission.result = JudgeStatus.ACCEPTED
        else:
            self.submission.result = error_test_cases[0]['result']

        self.submission.save()
        logger.info(f'Judge result: {self.submission.result} have beem saved.')

        # TODO: handle rank update for contest
        pass

    def _get_statistic_info(self, data: list[dict]):
        self.submission.statistic_info["time_cost"] = max(
            [x["cpu_time"] for x in data])
        self.submission.statistic_info["memory_cost"] = max(
            [x["memory"] for x in data])

        # TODO: calculate score for OI mode
        pass
