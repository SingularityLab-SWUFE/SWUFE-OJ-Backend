from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, UserProfile
import json
from django.core.cache import cache


class RegisterUserAPITest(TestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'test_user',
            'email': 'test_email@test.com',
            'password': 'test_password'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'test_user')
        self.assertEqual(response.data['email'], 'test_email@test.com')
        


class LogoutAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user.set_password('test_password')
        self.user.save()

        self.client = APIClient()
        self.token = str(self.user.get_token())
        self.url = reverse('logout')
        auth_header = 'Bearer ' + self.token
        self.client.credentials(HTTP_AUTHORIZATION=auth_header)
        cache.set(self.token, self.user, timeout=60*60*24)


    def test_logout(self):
        response = self.client.post(self.url, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_message = f"user:{self.user.username} has been logged out."
        self.assertEqual(response.data['data'], expected_message)
        self.assertFalse(cache.has_key(self.token))        


class LoginAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user.set_password('test_password')
        self.user.save()

        self.url = reverse('login')

    def test_login(self):
        data = {'username': 'test_user', 'password': 'test_password'}
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['data'])
        self.assertIn('user', response.data['data'])


class UserProfileAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user_profile = UserProfile.objects.create(user=self.user, real_name='xiaozhang')

        self.url = reverse('user-profile', kwargs={'username': 'test_user'})
        

    def test_get_user_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['real_name'], 'xiaozhang')


class EditUserProfileAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user_profile = UserProfile.objects.create(user=self.user)

        self.client = APIClient()

        self.url = reverse('edit-user-profile')
        self.token = str(self.user.get_token())
        auth_header = 'Bearer ' + self.token
        self.client.credentials(HTTP_AUTHORIZATION=auth_header)


    def test_edit_user_profile(self):
        data = {'real_name': 'xiaoming',
                'blog': 'https://xiaoming.xyz',
                'github': 'https://github.com/xiaoming',
                'school': 'SWUFE',
                'major': 'Computer Science',
                'language': 'Chinese'
                }
        response = self.client.put(
            self.url, json.dumps(data), content_type='application/json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['real_name'], 'xiaoming')
