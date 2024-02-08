# SWUFE-OJ 后端

技术栈: Python3.12 + Django 4.2 + MySQL 8.0.21

展望: 第二次奇点杯能用上自主开发的系统

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

可以的话再写一个在线自测功能

## 账号

- 个人主页面
- 修改主页面
- 展示近期通过的题目

## 题单

- 对题单的 CRUD 操作

- `GET /gym/<int:id>` 获取题单信息
  - 注意权限, 公开题单和私有题单(密码访问)
- `POST /gym` 创建题单
- `PUT /gym/<int:id>` 更新题单
- `DELETE /gym/<int:id>` 删除题单

## 比赛

- 创建比赛
  - CRUD contest
  - 私有比赛和公有比赛(权限)
  - 可选用户参赛或者团队参赛
  - 可以创建 vp
- 榜单
  - `GET /ranklist`
  - 显示用户过题数, 罚时等信息
- 赛制默认 ACM
  - 支持封榜机制
- (可选)和 [ICPC Tools](https://tools.icpc.global/) 的兼容(以后说不定拿来大屏幕滚榜)

## 讨论

- 开贴讨论
  - 需要一个讨论区(菜单栏里可以点击进入)
- 题目讨论
- 比赛讨论
- 站内消息系统
  - 比赛时消息
- 可以评论

大致架构: 创建一个帖子(post)

- 不同类别的讨论和不同的外键关联
  - 例如某一题目的帖子就和 problem_id 关联

## 远程评测

- 爬虫获取其它OJ平台题目
  - HDU, POJ, Codeforces(+gym)
  - 注意反爬取机制
- 将用户账号和其它 OJ 平台的账号做绑定
  - 注意[隐私](https://help.luogu.com.cn/manual/luogu/problem/remote-judge#%E9%9A%90%E7%A7%81%E6%94%BF%E7%AD%96)问题
  - 对用户密钥进行加密之类的
- 可选项: 创建各个平台的公有账号
  - 例如 vjudge1
- 服务器模拟用户提交
  - 获取提交 id, 爬取 submission 的信息
  - 同时创建一条 SWUFE-OJ 的一次提交

接口设计:

- `GET /remote/problems`
  - 参数: id, platform

获取某一平台某一 id 的题目
如果不带 id 就默认爬取全部页面

爬取策略: 每天刷新, 如果有新题目, 就写入数据库
也就是说爬取的题目我们放到自己的数据库里, 写入到 problems 表

- `POST /remote/bond` 绑定OJ账号
- `POST /remote/submission` 向远端服务器模拟用户提交代码
- `GET /remote/submission/<int:id>` 获取提交 id 的信息

## Redis 做缓存

- 数据缓存和评测队列优化
- 学就完了

## 超级管理员的后台优化

- 提供用户流量等数据

## 鸣谢

感谢下面的开源项目为 SWUFE-OJ 提供的参考

- [QDU OJ](https://github.com/QingdaoU/OnlineJudge)
- [HOJ](https://github.com/HimitZH/HOJ)
