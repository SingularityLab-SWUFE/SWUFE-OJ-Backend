import requests
import urllib.parse
import base64
import re
import json
import time
import os
import sys
import django
from bs4 import BeautifulSoup

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from problem.serializers import ProblemSerializer
from problem.models import Problem, ProblemTag


# Default headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
}


def post(url, data=None, para=None, headers=headers, cookies=None):
    try:
        # session = requests.Session()
        response = requests.post(
            url, data=data, params=para, headers=headers, cookies=cookies)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f'Exception raised when handling the POST request:\n {e}\n')
        return None


def get(url, para=None, headers=headers, cookies=None):
    try:
        response = requests.get(
            url, params=para, headers=headers, cookies=cookies)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response
    except requests.exceptions.RequestException as e:
        print(f'Exception raised when handling the GET request:\n {e}\n')
        return None


def user_login(username, userpass):
    '''
        HDU: 如果登录成功, 状态码返回 302 重定向, 否则 200
    '''
    login_data = {
        'username': username,
        'userpass': userpass,
        'login': 'Sign In'
    }
    login_para = {
        'action': 'login'
    }
    response = post('https://acm.hdu.edu.cn/userloginex.php',
                    data=login_data, para=login_para)
    return response


def submit(code, p_id, lang, cookies):
    '''
        提交代码, 需要用户的cookies
    '''
    url_encoded_code = urllib.parse.quote(code)
    encoded_code = base64.b64encode(url_encoded_code.encode()).decode()
    submit_data = {
        'check': 0,
        # 表单提交的代码经过 URL 编码, 再 Base64 编码
        '_usercode': encoded_code,
        'problemid': p_id,
        'language': lang
    }
    submit_para = {
        'action': 'submit'
    }
    response = post('https://acm.hdu.edu.cn/submit.php',
                    data=submit_data, para=submit_para, cookies=cookies)
    return response


def get_problem_info(pid, write=True, overwrite=False):
    '''
        获取题目信息
    '''
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
    problem_data = Problem.objects.filter(remote_id=pid, source="HDU").first()

    if problem_data is None or overwrite:
        delimiter = ["Problem Description", "Input",
                     "Output", "Sample Input", "Sample Output", "Source", "Author", "Hint"]

        response = get('https://acm.hdu.edu.cn/showproblem.php',
                       para={'pid': pid})
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
                    rich_text = f'<img style="max-width:100%;" src="{
                        img_src}">'
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
            "submission_statistics": submission_statistics,
            "problem_description": problem_description,
            "input_description": input_description,
            "output_description": output_description,
            "samples": samples,
            "source": source,
            "author": author,
            "hint": hint
        }
        json_data = json.dumps(data_dict, indent=4)
        if write and problem_data == None:
            problem_data = Problem(title=title, is_remote=True, remote_id=pid, source="HDU",
                                   description=problem_description, input=input_description,
                                   output=output_description, hint=hint, samples=samples, total_submission_number=submission_statistics[
                                       4],
                                   solved_submission_number=submission_statistics[5],
                                   standard_time_limit=submission_statistics[1],
                                   standard_memory_limit=submission_statistics[
                                       3], other_time_limit=submission_statistics[0],
                                   other_memory_limit=submission_statistics[2])
        elif overwrite:
            # update
            problem_data.total_submission_number = submission_statistics[4]
            problem_data.solved_submission_number = submission_statistics[5]
        problem_data.save()
        return json_data
    else:
        print(f"HDU {pid} data already in database.")
        return ProblemSerializer(problem_data).data


def get_submission_status(rid):
    submission_para = {
        'first': rid,
    }
    response = get('https://acm.hdu.edu.cn/status.php', para=submission_para)
    html_data = response.text
    soup = BeautifulSoup(html_data, 'html.parser')
    submission_info = {}

    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if cols[0].text.strip() == str(rid):
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

    json_data = json.dumps(submission_info, indent=4)
    return json_data


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

if __name__ == '__main__':
    # 更改为一个真实的杭电账号
    login_resp = user_login(username, password)
    print(login_resp.status_code)
    cookies = login_resp.cookies

    submit_resp = submit(sample_code, 1000, 0, cookies)
    raw_html = submit_resp.text

    matches = re.findall(r'<td height=22px>(\d+)<\/td>', raw_html)
    rid = matches[0]
    print(rid)
    # 延时 10s，等待远程评测机评测结束
    time.sleep(10)

    print(get_submission_status(rid))
    # 批量导入到数据库
    for i in range(1000, 1030):
        print(get_problem_info(i))
