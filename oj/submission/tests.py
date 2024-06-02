import os
import urllib.parse
import dramatiq
from django.test import TestCase, TransactionTestCase
from rest_framework.reverse import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from utils.api import APIClient
from utils.judger.dispatcher import JudgerDispatcher
from problem.models import Problem
from account.models import User, Role, UserProfile
from contest.models import Contest, ACMContestRank
from .models import Submission, JudgeStatus
from .tasks import judge

from problem.utils import create_test_case_zip, TestCaseZipProcessor

cpp_code = r'''#include <bits/stdc++.h>
using namespace std;
int main() {
    cout << "Hello SWUFE OJ!\n";
    return 0;
}
'''

wa_cpp_code = r'''#include <bits/stdc++.h>
using namespace std;
int main() {
    cout << "Hello SWUFE OJ.\n";
    return 0;
}
'''

test_problem = {
    "title": "Hello SWUFE OJ!",
    "description": "奇点工作室开发部的同学很高兴, 自己学校的 OJ 系统终于上线了. 现在需要你输出一个字符串表达奇点小伙伴们的心情.",
    "input": "本题无输入.",
    "output": "输出 `Hello SWUFE OJ!` 即可.",
    "samples": [{"input": None, "output": "Hello SWUFE OJ!"}],
    "standard_time_limit": 1000,
    "standard_memory_limit": 256
}

testcase = [
    {"filename": "1.in", "content": None},
    {"filename": "1.out", "content": "Hello SWUFE OJ!"}
]

contest_data = {
    "title": "Test Contest",
    "description": "This is a test contest",
    "start_time": "2021-01-01T00:00:00+08:00",
    "end_time": "2030-01-02T00:00:00+08:00",
    "visible": True,
}


class SubmissionTest(TransactionTestCase, TestCaseZipProcessor):
    def setUp(self):
        # create example problem
        self.filename = 'test.zip'
        self.problem = Problem.objects.create(**test_problem)
        zip_file = create_test_case_zip(self.filename, testcase)
        file = SimpleUploadedFile(self.filename, zip_file)
        _, test_case_id = self.process_zip(file, spj=False)
        self.problem.test_case_id = test_case_id
        self.problem.save()
        self.rsync_test_cases(test_case_id)

        self.user = User.objects.create(username='test')
        self.user_profile = UserProfile.objects.create(user=self.user)

        self.admin = User.objects.create(
            username='admin', admin_type=Role.ADMIN)
        self.contest = Contest.objects.create(
            **contest_data, created_by=self.admin, rule_type='ACM')
        self.contest_problem = Problem.objects.create(
            **test_problem, contest=self.contest, test_case_id=test_case_id)
        # register user to contest
        self.rank1 = ACMContestRank.objects.create(
            user=self.user, contest=self.contest)
        self.contestant = User.objects.create(username='contestant')
        UserProfile.objects.create(user=self.contestant)
        self.rank2 = ACMContestRank.objects.create(
            user=self.contestant, contest=self.contest)

        self.client = APIClient()
        self.client.token_auth(self.user)
        self.url = reverse('submit')
        # dramatiq setup
        self.broker = dramatiq.get_broker()
        self.worker = dramatiq.Worker(self.broker, worker_timeout=1000)
        self.worker.start()

    def test_submit_cpp_code(self):
        body = {"code": cpp_code, "problem_id": self.problem.id, "language": "C++"}
        url_encoded_data = urllib.parse.urlencode(body)
        response = self.client.post(
            self.url, url_encoded_data, content_type='application/x-www-form-urlencoded')

        self.assertIsNone(response.data['error'])
        data = response.data['data']
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['result'], JudgeStatus.PENDING)

        self.broker.join(judge.queue_name)
        self.worker.join()

        submission = Submission.objects.get(id=data['id'])
        self.assertEqual(submission.result, JudgeStatus.ACCEPTED)
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user.userprofile.solved_problem_number, 1)

    def test_submit_contest_problem(self):
        # submit to contest problem
        submission_data = {"code": cpp_code,
                           "problem_id": self.contest_problem.id, "language": "C++"}
        self.submission = Submission.objects.create(
            **submission_data, user=self.user)
        JudgerDispatcher(self.submission.id, self.contest_problem.id,
                         self.contest.id).judge()
        # contestant submit WA code
        WA_submission_data = {
            "code": wa_cpp_code, "problem_id": self.contest_problem.id, "language": "C++"}
        self.submission = Submission.objects.create(
            **WA_submission_data, user=self.contestant)
        JudgerDispatcher(self.submission.id, self.contest_problem.id,
                         self.contest.id).judge()

        url = reverse('contest_rank_api')
        resp = self.client.get(url, {'contest_id': self.contest.id})
        self.assertEqual(resp.data['error'], None)
        data = resp.data['data']
        # expecting 'test' to be first in the rank list
        self.assertEqual(data[0]['username'], self.user.username)

    # def test_compile_error(self):
    #     pass

    # def test_java_code(self):
    #     pass

    # def test_python_code(self):
    #     pass

    def tearDown(self):
        os.remove(self.filename)
        self.rsync_test_cases(self.problem.test_case_id, delete=True)
        self.worker.stop()
