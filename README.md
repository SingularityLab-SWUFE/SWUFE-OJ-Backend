# SWUFE-OJ 后端

技术栈: Python3.12 + Django 4.2 + MySQL

## 第一周实现

实现 a+b 的判题

### 建表

基本功能:

user, role, problem, tag, submission

题解/讨论部分:

solution, discussion, solution_comment, discussion_comment

TODO: 通过率

### 接口设计

注册登录登出 account

- `POST /signin`
- `POST /login`
- `POST /logout`

判题 problem

- 返回题目列表 `GET /problem`
- 返回题目具体 `GET /problem/<int:id>`

调取评测机接口 api

- 发送提交请求 `POST /submission/<int:user_id>`
- 返回提交的状态 `GET /submission/<string:id>`

前提是

- 把 judge server 配置好

如果不行先返回假数据
