from submission.models import Submission
from problem.models import Problem, ProblemTag
from problem.serializers import ProblemSerializer
import requests

OJ_URLS = {
    'HDU': 'https://acm.hdu.edu.cn/',
    'Codeforces': 'https://codeforces.com/',
    'Atcoder': 'https://atcoder.jp/'
}


class RequestSenderException(Exception):
    pass


class LoginException(Exception):
    pass


class RequestSender:
    '''
        Base class for remote oj request sender.
    '''

    def __init__(self, oj_name):
        '''
            Specify the remote online judge platform.
        '''
        self.oj_name = oj_name

        # Base url of the remote oj
        self.oj_url = OJ_URLS[oj_name]

        # Requests are passed through a session object to keep track of cookies and CSRF tokens
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'})
        self.cookies = None
        self.csrf_token = None

    def _get_auth(self):
        '''
            Mock login to get user authentication.

            The following private methods are required 
            implementation for each remote oj in subclass before calling basic APIs.
        '''
        pass

    def _get_submit_url(self, problem_id) -> str:
        pass

    def _get_submit_data(self, problem_id, code, lang) -> dict:
        pass

    def _get_submit_para(self) -> dict:
        pass

    def _get_submission_url(self, problem_id, submission_id) -> str:
        pass

    def _get_submission_para(self, submission_id) -> dict:
        pass

    def _get_problem_url(self, problem_id) -> str:
        pass

    def _get_problem_para(self, problem_id) -> dict:
        pass

    def _status_parser(self, response, submission_id) -> dict:
        pass

    def _problem_parser(self, response) -> dict:
        pass

    def submit(self, problem_id, code, lang):
        '''
            Submit code to a remote oj.
        '''
        self._get_auth()

        # url to submit code
        submit_url = self._get_submit_url(problem_id)

        # data that are passed to the url
        submit_data = self._get_submit_data(problem_id, code, lang)
        submit_para = self._get_submit_para()

        response = self.session.post(submit_url,
                                     data=submit_data, params=submit_para)

        return response

    def get_submission_info(self, submission_id, problem_id=None) -> dict:
        '''
            Get specific submission information from remote oj.
        '''
        if self.oj_name != 'HDU' and problem_id is None:
            raise RequestSenderException(
                "Problem id is required for non-HDU oj")

        # url of submission
        submission_url = self._get_submission_url(problem_id, submission_id)
        submission_para = self._get_submission_para(submission_id)

        response = self.session.get(submission_url, params=submission_para)

        # get submission info
        return self._status_parser(response, submission_id)

    def get_problem_info(self, problem_id, write=True):
        '''
            Get a specific problem information from remote oj.
            If `write` is True, then problem info will be written to database.
        '''
        # If data already exists in database, return it directly
        problem_data = Problem.objects.filter(
            remote_id=problem_id, source=self.oj_name).first()

        if problem_data is not None:
            return problem_data

        problem_url = self._get_problem_url(problem_id)
        problem_para = self._get_problem_para(problem_id)

        response = self.session.get(problem_url, params=problem_para)

        problem_info = self._problem_parser(response)

        if write:
            problem_info['remote_id'] = problem_id
            problem_info['source'] = self.oj_name
            problem_info['is_remote'] = True

            problem = Problem(**problem_info)
            problem.save()

        return problem_info
