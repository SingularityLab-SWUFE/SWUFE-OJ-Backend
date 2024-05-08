import hashlib
import json
import os
import zipfile
import subprocess
import random
import string
import re

from utils.api import APIError
from django.conf import settings
from django.utils.crypto import get_random_string


def rand_str(length=32, type="lower_hex"):
    if type == "str":
        return get_random_string(length, allowed_chars=string.ascii_uppercase+string.ascii_lowercase+string.digits)
    elif type == "lower_str":
        return get_random_string(length, allowed_chars=string.ascii_lowercase+string.digits)
    elif type == "lower_hex":
        return random.choice("123456789abcdef") + get_random_string(length - 1, allowed_chars=string.digits+"abcdef")
    else:
        return random.choice("123456789") + get_random_string(length - 1, allowed_chars=string.digits)


def natural_sort_key(s, _nsre=re.compile(r"(\d+)")):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def create_test_case_zip(zip_file_name: str, test_cases: list[dict], export_dir='.') -> bytes:
    '''
        Create a zip file of test cases in the given directory.

        Examples of test_cases:
        >>> [{'filename': '1.in', 'content': '1 2'}, {'filename': '1.out', 'content': '3'}]
    '''
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    full_zip_path = os.path.join(export_dir, zip_file_name)

    with zipfile.ZipFile(full_zip_path, 'w') as zipf:
        for file_info in test_cases:
            file_name = file_info['filename']
            file_content = file_info['content']
            if file_content is not None:
                zipf.writestr(file_name, file_content)
            else:
                with open(file_name, 'w') as f:
                    f.write('')
                zipf.write(file_name, arcname=file_name)
                os.remove(file_name)

    with open(full_zip_path, 'rb') as f:
        return f.read()


class TestCaseZipProcessor(object):
    def process_zip(self, uploaded_zip_file, spj=False, dir=""):
        try:
            zip_file = zipfile.ZipFile(uploaded_zip_file, "r")
        except zipfile.BadZipFile:
            raise APIError("Bad zip file")
        name_list = zip_file.namelist()
        test_case_list = self.filter_name_list(name_list, spj=spj, dir=dir)
        if not test_case_list:
            raise APIError("Empty file")

        test_case_id = rand_str()
        test_case_dir = os.path.join(settings.TEST_CASE_DIR, test_case_id)
        os.mkdir(test_case_dir)
        os.chmod(test_case_dir, 0o710)

        size_cache = {}
        md5_cache = {}

        for item in test_case_list:
            with open(os.path.join(test_case_dir, item), "wb") as f:
                content = zip_file.read(f"{dir}{item}").replace(b"\r\n", b"\n")
                size_cache[item] = len(content)
                if item.endswith(".out"):
                    md5_cache[item] = hashlib.md5(content.rstrip()).hexdigest()
                f.write(content)
        test_case_info = {"spj": spj, "test_cases": {}}

        info = []

        if spj:
            for index, item in enumerate(test_case_list):
                data = {"input_name": item, "input_size": size_cache[item]}
                info.append(data)
                test_case_info["test_cases"][str(index + 1)] = data
        else:
            # ["1.in", "1.out", "2.in", "2.out"] => [("1.in", "1.out"), ("2.in", "2.out")]
            test_case_list = zip(*[test_case_list[i::2] for i in range(2)])
            for index, item in enumerate(test_case_list):
                data = {"stripped_output_md5": md5_cache[item[1]],
                        "input_size": size_cache[item[0]],
                        "output_size": size_cache[item[1]],
                        "input_name": item[0],
                        "output_name": item[1]}
                info.append(data)
                test_case_info["test_cases"][str(index + 1)] = data

        with open(os.path.join(test_case_dir, "info"), "w", encoding="utf-8") as f:
            f.write(json.dumps(test_case_info, indent=4))

        for item in os.listdir(test_case_dir):
            os.chmod(os.path.join(test_case_dir, item), 0o640)

        return info, test_case_id

    def filter_name_list(self, name_list, spj, dir=""):
        '''
            Get sorted(natural_sort) test case list from name_list. e.g.
            >>> processor.filter_name_list(['2.in', '1.in', '2.out', '1.out'], spj=False)
            ['1.in', '1.out', '2.in', '2.out']
        '''
        ret = []
        prefix = 1
        if spj:
            while True:
                in_name = f"{prefix}.in"
                if f"{dir}{in_name}" in name_list:
                    ret.append(in_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret, key=natural_sort_key)
        else:
            while True:
                in_name = f"{prefix}.in"
                out_name = f"{prefix}.out"
                if f"{dir}{in_name}" in name_list and f"{dir}{out_name}" in name_list:
                    ret.append(in_name)
                    ret.append(out_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret, key=natural_sort_key)

    def rsync_test_cases(self, test_case_id, delete=False):
        if test_case_id is None:
            raise APIError("Testcase id cannot be empty")

        # TODO: if multiple judgers exist, rsync test case to all judgers
        src_dir = f'{settings.TEST_CASE_DIR}/{test_case_id}/'
        dst_dir = f'root@{settings.JUDGE_SERVER_HOST}:{
            settings.JUDGE_SERVER_TEST_CASE_DIR}/{test_case_id}/'

        rsync_command = ['rsync', '-avz', '-e', 'ssh', src_dir, dst_dir]
        # delete test case on judge server
        unlink_command = ['ssh', f'root@{settings.JUDGE_SERVER_HOST}',
                          'rm', '-rf', f'{settings.JUDGE_SERVER_TEST_CASE_DIR}/{test_case_id}']

        command = rsync_command if not delete else unlink_command

        try:
            result = subprocess.run(command, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode()
        except subprocess.CalledProcessError as e:
            raise Exception(f"rsync failed: {e.stderr.decode()}")
