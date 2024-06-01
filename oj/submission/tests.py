import os
import urllib.parse
import dramatiq
from django.test import TestCase, TransactionTestCase
from rest_framework.reverse import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from utils.api import APIClient
from problem.models import Problem
from account.models import User, UserProfile
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

    def test_compile_error(self):
        pass

    def test_java_code(self):
        pass

    def test_python_code(self):
        pass

    def tearDown(self):
        os.remove(self.filename)
        self.rsync_test_cases(self.problem.test_case_id, delete=True)
        self.worker.stop()
