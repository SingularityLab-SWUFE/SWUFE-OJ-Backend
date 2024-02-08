import requests
import urllib.parse
import base64
import re
import json
import time
from bs4 import BeautifulSoup

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
