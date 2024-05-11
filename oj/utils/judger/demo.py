'''
    This is a demo program to show how to use the JudgeServerClient.
    In this directory, run python demo.py to see the output.
'''

import sys
import os
import django
from client import JudgeServerClient
from config import *
from django.conf import settings

sys.path.append('../..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

if __name__ == "__main__":

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
        token=settings.JUDGE_SERVER_TOKEN, server_base_url=f"http://{settings.JUDGE_SERVER_HOST}:{settings.JUDGE_SERVER_PORT}")
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
