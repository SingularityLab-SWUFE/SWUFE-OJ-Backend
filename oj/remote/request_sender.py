from submission.models import Submission
from problem.models import Problem, ProblemTag
from problem.serializers import ProblemSerializer
import requests

OJ_URLS = {
    'HDU': 'https://acm.hdu.edu.cn/',
    'Codeforces': 'https://codeforces.com/',
    'Atcoder': 'https://atcoder.jp/'
}


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
        self.cookies = None
        self.csrf_token = None

    def get_auth(self):
        '''
            Mock login to get user authentication.

            The following methods are required 
            implementation for each remote oj in subclass before calling basic APIs.
        '''
        pass

    def get_submit_url(self, problem_id) -> str:
        pass

    def get_submit_data(self, problem_id, code, lang) -> dict:
        pass

    def get_submit_para(self) -> dict:
        pass

    def get_submission_url(self, problem_id, submission_id) -> str:
        pass

    def get_submission_para(self, submission_id):
        pass
    
    def get_problem_url(self, problem_id) -> str:
        pass
    
    def get_problem_para(self, problem_id) -> dict:
        pass

    def status_parser(self, response, submission_id) -> dict:
        pass
    
    def problem_parser(self, response):
        '''
            Parse problem information from remote oj response.
        '''
        pass
    
    def submit(self, problem_id, code, lang):
        '''
            Submit code to a remote oj.
        '''
        self.get_auth()

        # url to submit code
        submit_url = self.get_submit_url(problem_id)

        # data that are passed to the url
        submit_data = self.get_submit_data(problem_id, code, lang)
        submit_para = self.get_submit_para()

        response = self.session.post(submit_url,
                                     data=submit_data, params=submit_para)

        return response


    def get_submission_info(self, submission_id, problem_id=None) -> dict:
        '''
            Get specific submission information from remote oj.
        '''
        if self.oj_name != 'HDU':
            assert problem_id is not None, "Problem id is required for non-HDU oj."
            
        # url of submission
        submission_url = self.get_submission_url(problem_id, submission_id)
        submission_para = self.get_submission_para(submission_id)
        
        response = self.session.get(submission_url, params=submission_para)
        
        # get submission info
        return self.status_parser(response, submission_id)


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

        problem_url = self.get_problem_url(problem_id)
        problem_para = self.get_problem_para(problem_id)
        
        response = self.session.get(problem_url, params=problem_para)
        
        problem_info = self.problem_parser(response)
        
        if write:
            problem_info['remote_id'] = problem_id
            problem_info['source'] = self.oj_name
            
            problem = Problem(**problem_info)
            problem.save()
            
        return problem_info
