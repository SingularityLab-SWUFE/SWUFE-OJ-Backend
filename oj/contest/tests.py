from urllib.parse import urlencode
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from utils.api import APIClient
from .models import Contest
from account.models import User, Role
from problem.models import Problem

contest_data = {
    "title": "Test Contest",
    "description": "This is a test contest",
    "start_time": "2021-01-01T00:00:00+08:00",
    "end_time": "2021-01-02T00:00:00+08:00",
    "password": "test",
    "visible": True,
}


class ContestTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            username='admin', admin_type=Role.ADMIN)
        self.client.token_auth(self.admin_user)
        self.url = reverse('contest_admin_api')

    def test_create_contest(self):
        encoded_data = urlencode(contest_data)
        resp = self.client.post(self.url, encoded_data,
                                content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.data['error'], None)
        data = resp.data['data']
        self.assertEqual(data['title'], contest_data['title'])
        self.assertEqual(data['description'], contest_data['description'])
        self.assertEqual(data['start_time'], contest_data['start_time'])
        self.assertEqual(data['end_time'], contest_data['end_time'])
        self.assertEqual(data['password'], contest_data['password'])
        self.assertEqual(data['visible'], contest_data['visible'])
        contest = Contest.objects.get(title=contest_data['title'])
        self.assertEqual(data['title'], contest.title)
        self.assertEqual(contest.created_by.username,
                         self.admin_user.username)

    def test_update_contest(self):
        contest = Contest.objects.create(
            **contest_data, created_by=self.admin_user)
        update_data = {
            "id": contest.id,
            "title": "Updated Test Contest",
            "description": " This contest has been updated",
            "start_time": "2021-01-02T00:00:00+08:00",
            "end_time": "2021-01-03T00:00:00+08:00",
        }
        encoded_data = urlencode(update_data)
        resp = self.client.put(self.url, encoded_data,
                               content_type='application/x-www-form-urlencoded')

        self.assertEqual(resp.data['error'], None)
        data = resp.data['data']
        self.assertEqual(data['title'], update_data['title'])
        self.assertEqual(data['description'], update_data['description'])
        self.assertEqual(data['start_time'], update_data['start_time'])
        self.assertEqual(data['end_time'], update_data['end_time'])


class ContestViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            username='admin', admin_type=Role.ADMIN)
        self.url = reverse('contest_view_api')

    def test_get_contest(self):
        contest = Contest.objects.create(
            **contest_data, created_by=self.admin_user)

        # Login with password
        resp = self.client.get(self.url, {'contest_id': contest.id,
                                          'password': contest_data['password']})
        self.assertEqual(resp.data['error'], None)
        data = resp.data['data']
        self.assertEqual(data['title'], contest.title)

        # Login without password
        resp = self.client.get(self.url, {'id': contest.id})
        self.assertEqual(resp.data['error'], "error")
        self.assertEqual(resp.data['data'], "Password is required")

        # Login with wrong password
        resp = self.client.get(self.url, {'contest_id': contest.id,
                                          'password': 'wrong'})
        self.assertEqual(resp.data['error'], "error")
        self.assertEqual(resp.data['data'], "Password is incorrect")

class ContestRegisterTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            username='admin', admin_type=Role.ADMIN)
        self.contestant = User.objects.create(
            username='contestant1', admin_type=Role.REGULAR_USER)

    def test_register_contest(self):
        pass

class ContestRankTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_acm_rank(self):
        pass
    
    def test_oi_rank(self):
        pass
