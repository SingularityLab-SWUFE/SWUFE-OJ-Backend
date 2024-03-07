# coding=utf-8
from __future__ import unicode_literals
import hashlib
import json

import requests


default_env = ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]


c_lang_config = {
    "compile": {
        "src_name": "main.c",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 128 * 1024 * 1024,
        "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c99 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": "c_cpp",
        "env": default_env
    }
}

c_lang_spj_compile = {
    "src_name": "spj-{spj_version}.c",
    "exe_name": "spj-{spj_version}",
    "max_cpu_time": 3000,
    "max_real_time": 5000,
    "max_memory": 1024 * 1024 * 1024,
    "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c99 {src_path} -lm -o {exe_path}"
}

c_lang_spj_config = {
    "exe_name": "spj-{spj_version}",
    "command": "{exe_path} {in_file_path} {user_out_file_path}",
    "seccomp_rule": "c_cpp"
}

cpp_lang_config = {
    "compile": {
        "src_name": "main.cpp",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 128 * 1024 * 1024,
        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}",
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": "c_cpp",
        "env": default_env
    }
}

java_lang_config = {
    "name": "java",
    "compile": {
        "src_name": "Main.java",
        "exe_name": "Main",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": -1,
        "compile_command": "/usr/bin/javac {src_path} -d {exe_dir} -encoding UTF8"
    },
    "run": {
        "command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k -Djava.security.manager -Dfile.encoding=UTF-8 -Djava.security.policy==/etc/java_policy -Djava.awt.headless=true Main",
        "seccomp_rule": None,
        "env": default_env,
        "memory_limit_check_only": 1
    }
}


py2_lang_config = {
    "compile": {
        "src_name": "solution.py",
        "exe_name": "solution.pyc",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 128 * 1024 * 1024,
        "compile_command": "/usr/bin/python -m py_compile {src_path}",
    },
    "run": {
        "command": "/usr/bin/python {exe_path}",
        "seccomp_rule": "general",
        "env": default_env
    }
}

py3_lang_config = {
    "compile": {
        "src_name": "solution.py",
        "exe_name": "__pycache__/solution.cpython-36.pyc",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 128 * 1024 * 1024,
        "compile_command": "/usr/bin/python3 -m py_compile {src_path}",
    },
    "run": {
        "command": "/usr/bin/python3 {exe_path}",
        "seccomp_rule": "general",
        "env": ["PYTHONIOENCODING=UTF-8"] + default_env
    }
}

go_lang_config = {
    "compile": {
        "src_name": "main.go",
        "exe_name": "main",
        "max_cpu_time": 3000,
        "max_real_time": 5000,
        "max_memory": 1024 * 1024 * 1024,
        "compile_command": "/usr/bin/go build -o {exe_path} {src_path}",
        "env": ["GOCACHE=/tmp", "GOPATH=/tmp/go"]
    },
    "run": {
        "command": "{exe_path}",
        "seccomp_rule": "",
        # 降低内存占用
        "env": ["GODEBUG=madvdontneed=1", "GOCACHE=off"] + default_env,
        "memory_limit_check_only": 1
    }
}

php_lang_config = {
    "run": {
        "exe_name": "solution.php",
        "command": "/usr/bin/php {exe_path}",
        "seccomp_rule": "",
        "env": default_env,
        "memory_limit_check_only": 1
    }
}

js_lang_config = {
    "run": {
        "exe_name": "solution.js",
        "command": "/usr/bin/node {exe_path}",
        "seccomp_rule": "",
        "env": ["NO_COLOR=true"] + default_env,
        "memory_limit_check_only": 1
    }
}


class JudgeServerClientError(Exception):
    pass


class JudgeServerClient(object):
    def __init__(self, token, server_base_url):
        self.token = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.server_base_url = server_base_url.rstrip("/")

    def _request(self, url, data=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token,
                              "Content-Type": "application/json"}}
        if data:
            kwargs["data"] = json.dumps(data)
        try:
            return requests.post(url, **kwargs).json()
        except Exception as e:
            raise JudgeServerClientError(str(e))

    def ping(self):
        return self._request(self.server_base_url + "/ping")

    def judge(self, src, language_config, max_cpu_time, max_memory, test_case_id=None, test_case=None, spj_version=None, spj_config=None,
              spj_compile_config=None, spj_src=None, output=False):
        if not (test_case or test_case_id) or (test_case and test_case_id):
            raise ValueError("invalid parameter")

        data = {"language_config": language_config,
                "src": src,
                "max_cpu_time": max_cpu_time,
                "max_memory": max_memory,
                "test_case_id": test_case_id,
                "test_case": test_case,
                "spj_version": spj_version,
                "spj_config": spj_config,
                "spj_compile_config": spj_compile_config,
                "spj_src": spj_src,
                "output": output}
        return self._request(self.server_base_url + "/judge", data=data)

    def compile_spj(self, src, spj_version, spj_compile_config):
        data = {"src": src, "spj_version": spj_version,
                "spj_compile_config": spj_compile_config}
        return self._request(self.server_base_url + "/compile_spj", data=data)


if __name__ == "__main__":
    token = "I_LOVE_SWUFE"

    c_src = r"""
    #include <stdio.h>
    int main(){
        int a, b;
        scanf("%d%d", &a, &b);
        printf("%d\n", a+b);
        return 0;
    }
    """

    c_spj_src = r"""
    #include <stdio.h>
    int main(){
        return 1;
    }
    """

    cpp_src = r"""
    #include <iostream>

    using namespace std;

    int main()
    {
        int a,b;
        cin >> a >> b;
        cout << a+b << endl;
        return 0;
    }
    """

    java_src = r"""
    import java.util.Scanner;
    public class Main{
        public static void main(String[] args){
            Scanner in=new Scanner(System.in);
            int a=in.nextInt();
            int b=in.nextInt();
            System.out.println(a + b);
        }
    }
    """

    py2_src = """s = raw_input()
s1 = s.split(" ")
print int(s1[0]) + int(s1[1])"""

    py3_src = """s = input()
s1 = s.split(" ")
print(int(s1[0]) + int(s1[1]))"""

    go_src = """package main
import "fmt"

func main() {
    a := 0
    b := 0
    fmt.Scanf("%d %d", &a, &b)
    fmt.Printf("%d", a + b)
}"""

    php_src = """<?php
fscanf(STDIN, "%d %d", $a, $b);
print($a + $b);"""

    js_src = """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (input) => {
  if (input === '') {
    return rl.close();
  }
  const [a, b] = input.split(' ').map(Number)
  console.log(a + b);
});"""

    client = JudgeServerClient(
        token=token, server_base_url="http://81.70.47.30:12358")
    print("ping")
    print(client.ping(), "\n\n")

    print("compile_spj")
    print(client.compile_spj(src=c_spj_src, spj_version="2", spj_compile_config=c_lang_spj_compile
                             ), "\n\n")

    print("c_judge")
    print(client.judge(src=c_src, language_config=c_lang_config,
                       max_cpu_time=1000, max_memory=1024 * 1024 * 128,
                       test_case_id="normal", output=True), "\n\n")

    print("cpp_judge")
    print(client.judge(src=cpp_src, language_config=cpp_lang_config,
                       max_cpu_time=1000, max_memory=1024 * 1024 * 128,
                       test_case_id="normal"), "\n\n")

    print("java_judge")
    print(client.judge(src=java_src, language_config=java_lang_config,
                       max_cpu_time=1000, max_memory=256 * 1024 * 1024,
                       test_case_id="normal"), "\n\n")

    print("c_spj_judge")
    print(client.judge(src=c_src, language_config=c_lang_config,
                       max_cpu_time=1000, max_memory=1024 * 1024 * 128,
                       test_case_id="spj",
                       spj_version="3", spj_config=c_lang_spj_config,
                       spj_compile_config=c_lang_spj_compile, spj_src=c_spj_src), "\n\n")

    print("py2_judge")
    print(client.judge(src=py2_src, language_config=py2_lang_config,
                       max_cpu_time=1000, max_memory=128 * 1024 * 1024,
                       test_case_id="normal", output=True), "\n\n")

    print("py3_judge")
    print(client.judge(src=py3_src, language_config=py3_lang_config,
                       max_cpu_time=1000, max_memory=128 * 1024 * 1024,
                       test_case_id="normal", output=True), "\n\n")

    print("go_judge")
    print(client.judge(src=go_src, language_config=go_lang_config,
                       max_cpu_time=1000, max_memory=128 * 1024 * 1024,
                       test_case_id="normal", output=True), "\n\n")

    print("php_judge")
    print(client.judge(src=php_src, language_config=php_lang_config,
                       max_cpu_time=1000, max_memory=128 * 1024 * 1024,
                       test_case_id="normal", output=True), "\n\n")

    print("js_judge")
    print(client.judge(src=js_src, language_config=js_lang_config,
                       max_cpu_time=1000, max_memory=128 * 1024 * 1024,
                       test_case_id="normal", output=True), "\n\n")

    print("c_dynamic_input_judge")
    print(client.judge(src=c_src, language_config=c_lang_config,
                       max_cpu_time=1000, max_memory=1024 * 1024 * 128,
                       test_case=[{"input": "1 2\n", "output": "3"}, {"input": "1 4\n", "output": "3"}], output=True), "\n\n")
