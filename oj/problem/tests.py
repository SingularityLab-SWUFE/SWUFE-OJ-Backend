import urllib
import json
import os
from django.test import TestCase
from rest_framework.reverse import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from utils.api import APIClient
from account.models import User, Role
from contest.models import Contest

from .serializers import TestCaseUploadForm
from .models import Problem, ProblemSet
from .utils import create_test_case_zip, TestCaseZipProcessor

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

encoded_data = urllib.parse.urlencode(test_problem)


class ProblemCreateAPITest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create(
            username='admin', admin_type=Role.ADMIN)
        self.student = User.objects.create(
            username='student', admin_type=Role.REGULAR_USER)
        self.client = APIClient()

    def test_get_problem_by_id(self):
        self.problem = Problem.objects.create(**test_problem)

        self.url = reverse('get_problem', args=[self.problem.id])

        response = self.client.get(self.url)
        data = response.data['data']
        self.assertEqual(data['title'], test_problem['title'])

    def test_create_problem(self):
        self.url = reverse('create_problem')
        self.client.token_auth(self.admin_user)

        response = self.client.post(
            self.url, encoded_data, content_type='application/x-www-form-urlencoded'
        )

        data = response.data['data']
        self.assertEqual(data['title'], test_problem['title'])
        self.assertEqual(data['is_remote'], False)

    def test_create_problem_validator(self):
        self.url = reverse('create_problem')
        self.client.token_auth(self.admin_user)

        test_problem_2 = test_problem.copy()
        # Ask for 2GB, NOT ALLOWED
        test_problem_2['standard_memory_limit'] = 2048
        encoded_data_2 = urllib.parse.urlencode(test_problem_2)
        response = self.client.post(
            self.url, encoded_data_2, content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.data['error'], 'error')

    def test_create_problem_no_permission(self):
        self.url = reverse('create_problem')
        self.client.token_auth(self.student)

        response = self.client.post(
            self.url, encoded_data, content_type='application/x-www-form-urlencoded'
        )

        data = response.data['data']
        self.assertEqual(response.data['error'], 'error')
        self.assertEqual(data, '一般用户没有权限创建题目')

    def tearDown(self):
        Problem.objects.all().delete()


class ProblemListAPITest(TestCase):
    def setUp(self):
        # mock data
        self.admin = User.objects.create(
            username='admin', admin_type=Role.ADMIN)
        self.contest = Contest.objects.create(
            title='contest1', start_time='2021-01-01T00:00:00+08:00', end_time='2029-01-02T00:00:00+08:00', created_by=self.admin)
        self.p1 = Problem.objects.create(title='p1', is_remote=True, remote_id=1000, source="HDU", difficulty="Easy", description="desc1",
                                         input="input1", output="output1", samples=[{"input": "input1", "output": "output1"}], contest=self.contest)
        self.p2 = Problem.objects.create(title='p2', is_remote=True, remote_id=1001, source="HDU", difficulty="Easy", description="desc2",
                                         input="input2", output="output2", samples=[{"input": "input2", "output": "output2"}])
        self.p3 = Problem.objects.create(title='p3', is_remote=False, difficulty="Hard", description="desc3",
                                         input="input3", output="output3", samples=[{"input": "input3", "output": "output3"}])
        self.client = APIClient()
        self.url = reverse('get_problem_list')

    def tearDown(self):
        Problem.objects.all().delete()

    def test_filter_by_remote(self):
        params = {'is_remote': True}
        response = self.client.get(self.url, params)
        data = response.data['data']
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], self.p1.title)
        self.assertEqual(data[1]['title'], self.p2.title)

    def test_filter_by_difficulty(self):
        params = {'difficulty': 'Hard'}
        response = self.client.get(self.url, params)
        data = response.data['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.p3.title)

    def test_filter_by_keyword(self):
        params = {'keyword': 'p1'}
        response = self.client.get(self.url, params)
        data = response.data['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.p1.title)

    def test_filter_by_contest(self):
        params = {'contest_id': self.contest.id}
        response = self.client.get(self.url, params)
        data = response.data['data']
        self.assertEqual(data[0]['title'], self.p1.title)


class TestCaseAPITest(TestCase, TestCaseZipProcessor):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='test', admin_type=Role.ADMIN)
        self.client.token_auth(self.user)
        self.filename = "test_case.zip"
        self.url = reverse('create_testcase')

    def test_create_testcase(self):
        problem = Problem.objects.create(**test_problem)
        zip_file = create_test_case_zip(self.filename, testcase)

        response = self.client.post(
            self.url, {'test_cases': SimpleUploadedFile(
                self.filename, zip_file), "spj": "false"},
            QUERY_STRING='problem_id={}'.format(problem.id),)

        data = response.data['data']
        self.assertEqual(data['spj'], False)
        self.assertIsNotNone(data['info'])
        self.assertIsNotNone(data['test_case_id'])
        problem = Problem.objects.get(id=problem.id)
        self.assertEqual(data['test_case_id'], problem.test_case_id)

        self.rsync_test_cases(data['test_case_id'], delete=True)
        os.remove(self.filename)


class ProblemSetAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='test', admin_type=Role.ADMIN)
        self.client.token_auth(self.user)
        self.problem = Problem.objects.create(**test_problem)
        self.url = reverse('create_problem_set')

    def test_create_problem_set(self):
        problem_set_info = {
            'name': "test set",
            'description': "test set description",
            'problems': [self.problem.id]
        }
        request_data = json.dumps(problem_set_info)
        response = self.client.post(
            self.url, request_data, content_type='application/json')
        data = response.data['data']
        self.assertEqual(data['name'], problem_set_info['name'])
        self.assertEqual(data['description'], problem_set_info['description'])

    def test_add_problem_to_set(self):
        problem_set_info = {
            'name': "test set",
            'description': "test set description",
            'created_by': self.user
        }
        problem_set = ProblemSet.objects.create(**problem_set_info)
        problem_set.problems_included.set([self.problem])
        self.assertEqual(problem_set.problems_included.count(), 1)
        test_problem_2 = test_problem.copy()
        test_problem_2['title'] = 'new test problem'
        new_problem = Problem.objects.create(**test_problem_2)

        request_data = json.dumps({'name': 'Updated problem set',
                                   'problem_set_id': problem_set.id,
                                   'problems': [self.problem.id, new_problem.id]})
        response = self.client.put(
            reverse('create_problem_set'), request_data, content_type='application/json')
        self.assertEqual(response.data['error'], None)
        data = response.data['data']
        self.assertEqual(data['name'], 'Updated problem set')
        self.assertEqual(data['problems_included'], [
                         self.problem.id, new_problem.id])

        # No permission to update
        user = User.objects.create(username='test2')
        self.client.token_auth(user)
        response = self.client.put(
            reverse('create_problem_set'), request_data, content_type='application/json')
        self.assertEqual(response.data['error'], 'error')
