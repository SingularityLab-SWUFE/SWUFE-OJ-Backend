# SWUFE-OJ 后端

技术栈: Django + MySQL

## 第一周实现

实现 a+b 的判题

接口：

建表: user, role, problem, tag, submission

solution, discussion, solution_comment, discussion_comment

TODO: 通过率

- 注册登录登出
- `POST /signin`
- `POST /login`
- `POST /logout`

判题

- 返回题目列表 `GET /problem`
- 返回题目具体 `GET /problem/<int:id>`
- 返回提交的状态 `GET /submission/<string:id>`

前提是

- 把 judge server 配置好

如果不行先返回假数据
