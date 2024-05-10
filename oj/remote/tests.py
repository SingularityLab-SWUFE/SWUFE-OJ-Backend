from django.test import TestCase
from problem.models import Problem

from .hdu import HDUSender

sample_code = r'''#include <iostream>
using namespace std;
int main()
{
   int a, b;
   while (cin >> a >> b)
   {
       cout << a + b << '\n';
   }
   return 0;
}'''


class HduRequestTest(TestCase):
    def setUp(self):
        self.client = HDUSender()

    def test_login(self):
        self.client._get_auth()

        # print('validating cookies:', self.client.cookies.get_dict())
        self.assertNotEqual(self.client.cookies, None)

    def test_submit_code(self):
        '''
            Test for submitting code to HDU.
        '''
        resp = self.client.submit(1000, code=sample_code, lang='G++')

        self.assertEqual(resp.status_code, 200)
        print(resp.text) # debug

        rid = self.client._get_submission_id(resp)
        # print('Submission has been sent with rid:', rid)
        self.assertIsNotNone(rid)

    def test_get_status(self):
        '''
            Test for getting status of a submission.
        '''
        rid = 39336558
        info = self.client.get_submission_info(rid)
        # print(info)
        self.assertNotEqual(info, {})


    def test_get_problem_info(self):
        '''
            Test for getting problem information.
        '''
        pid = 1000
        info = self.client.get_problem_info(pid, write=False)
        self.assertNotEqual(info, {})

    
    def test_write_problem(self):
        '''
            Test for writing remote hdu problem to database.
        '''
        pid = 1000
        info = self.client.get_problem_info(pid, write=True)
        self.assertNotEqual(info, {})
        problem = Problem.objects.filter(remote_id=pid, source="HDU").first()
        self.assertIsNotNone(problem)
        