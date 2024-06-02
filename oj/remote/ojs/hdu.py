from ..utils import RequestSender, LoginException
from urllib.parse import quote
from django.conf import settings
from django.core import serializers

import re
import base64
from bs4 import BeautifulSoup


class HDUSender(RequestSender):
    def __init__(self):
        super().__init__('HDU')

    def _get_auth(self):
        login_data = {
            # using public account to login in
            'username': settings.HDU_ACCOUNT,
            'userpass': settings.HDU_PASSWORD,
            'login': 'Sign In'
        }
        login_para = {
            'action': 'login'
        }
        response = self.session.post('https://acm.hdu.edu.cn/userloginex.php',
                                     data=login_data, params=login_para)

        if response.status_code != 302:
            raise LoginException('Failed to login in HDU')
        
        self.cookies = response.cookies

    def _get_submit_url(self, problem_id) -> str:
        # fixed submit endpoint for HDU
        return self.oj_url + 'submit.php'

    def _get_submit_data(self, problem_id, code, lang) -> dict:
        url_encoded_code = quote(code)
        encoded_code = base64.b64encode(url_encoded_code.encode()).decode()

        language_type = {
            'G++': 0,
            'GCC': 1,
            'C++': 2,
            'C': 3,
            'Pascal': 4,
            'Java': 5,
            'C#': 6
        }
        return {
            '_usercode': encoded_code,
            'problemid': problem_id,
            'language': language_type[lang]
        }

    def _get_submit_para(self) -> dict:
        return {
            'action': 'submit',
        }

    def _get_submission_id(self, response):
        '''
            Parse submission response to get submission id.
        '''
        matches = re.findall(r'<td height=22px>(\d+)<\/td>', response.text)
        # print(matches)
        try:
            rid = matches[0]
        except IndexError:
            rid = None
        
        return rid

    def _get_submission_url(self, problem_id, submission_id) -> str:
        # fixed for HDU
        return self.oj_url + 'status.php'

    def _get_submission_para(self, submission_id):
        return {
            'first': submission_id,
            'user': settings.HDU_ACCOUNT,
        }

    def _status_parser(self, response, submission_id) -> dict:
        soup = BeautifulSoup(response.text, 'html.parser')
        submission_info = {}
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if cols[0].text.strip() == str(submission_id):
                submission_info = {
                    "Run ID": cols[0].text.strip(),
                    "Timestamp": cols[1].text.strip(),
                    "Status": cols[2].text.strip(),
                    "Problem ID": cols[3].text.strip(),
                    "Time": cols[4].text.strip(),
                    "Memory": cols[5].text.strip(),
                    "Code Size": cols[6].text.strip(),
                    "Language": cols[7].text.strip(),
                    "User": cols[8].text.strip()
                }
        return submission_info
        # return serializers.serialize('json', submission_info)

    def _get_problem_url(self, problem_id) -> str:
        return self.oj_url + 'showproblem.php'

    def _get_problem_para(self, problem_id) -> dict:
        return {
            'pid': problem_id,
        }

    def _problem_parser(self, response) -> dict:
        title = ""
        problem_description = ""
        input_description = ""
        output_description = ""
        samples = []
        input_sample = ""
        output_sample = ""
        source = ""
        author = ""
        hint = ""

        delimiter = ["Problem Description", "Input",
                     "Output", "Sample Input", "Sample Output", "Source", "Author", "Hint"]

        # 将 <br> 转写成 \n
        html_data = response.text.replace("<br>", '\n')
        soup = BeautifulSoup(html_data, 'html.parser')
        cleaned_soup = soup.find_all(
            'td', attrs={'align': 'center'})
        # 题目名称
        title = soup.find('h1', style="color:#1A5CC8").get_text(strip=True)
        # HDU 的提交信息
        submission_info = soup.find(
            'span', style='font-family:Arial;font-size:12px;font-weight:bold;color:green').get_text(strip=True)
        submission_statistics = re.findall(
            r'\d+', submission_info)

        rich_text, cur = "", ""
        for s in cleaned_soup:
            # s: bs4.element.Tag
            for tag in s.find_all(['div', 'img']):
                # 获取全部 div 标签
                # 带 class 防止样例部分重复获取子标签
                if tag.name == 'div' and 'class' in tag.attrs:
                    rich_text = tag.get_text()
                # 提取正文图片的地址
                # 可能以后会把图片存到自己的数据库里
                elif tag.name == 'img' and 'style' in tag.attrs:
                    img_name = re.search(r'/([^/]+)$', tag['src']).group(1)
                    img_src = f"https://acm.hdu.edu.cn/data/images/{img_name}"
                    rich_text = f'<img style="max-width:100%;"\
                        src="{img_src}">'
                else:
                    continue

                if rich_text in delimiter:
                    cur = rich_text
                else:
                    if cur == delimiter[0]:
                        problem_description += rich_text
                    elif cur == delimiter[1]:
                        input_description += rich_text
                    elif cur == delimiter[2]:
                        output_description += rich_text
                    elif cur == delimiter[3]:
                        input_sample += rich_text
                    elif cur == delimiter[4]:
                        output_sample += rich_text
                    elif cur == delimiter[5]:
                        source += rich_text
                    elif cur == delimiter[6]:
                        author += rich_text
                    elif cur == delimiter[6]:
                        hint += rich_text

        # HDU 只有一个 sample
        samples = [{"input": input_sample, "output": output_sample}]
        data_dict = {
            "title": title,
            "total_submission_number": submission_statistics[4],
            "solved_submission_number": submission_statistics[5],
            "standard_time_limit": submission_statistics[1],
            # hdu uses kb, convert to mb
            "standard_memory_limit": int(submission_statistics[3]) // 1024,
            "other_time_limit": submission_statistics[0],
            "other_memory_limit": int(submission_statistics[2]) // 1024,
            "description": problem_description,
            "input": input_description,
            "output": output_description,
            "samples": samples,
            "hint": hint
        }

        return data_dict

    # APIs
    def submit(self, problem_id, code, lang):
        return super().submit(problem_id, code, lang)

    def get_submission_info(self, submission_id, problem_id=None) -> dict:
        return super().get_submission_info(submission_id, problem_id)

    def get_problem_info(self, problem_id, write=True):
        return super().get_problem_info(problem_id, write)
