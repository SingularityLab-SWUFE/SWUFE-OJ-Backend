# SWUFE-OJ 后端

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/SingularityLab-SWUFE/SWUFE-OJ-Backend)

![GitHub last commit](https://img.shields.io/github/last-commit/SingularityLab-SWUFE/SWUFE-OJ-Backend)

技术栈: Python3.12 + Django 4.2 + MySQL 8.0.21 + Redis + Docker

在线文档: [gitbook](https://singularity-backend.gitbook.io/backend-online-doc/swufe-oj/readme)

主要 features:

- 前后端分离项目
- 支持虚拟远程评测(vjudge), 包括 HDU, Codeforces 等主流平台
- 题解/讨论区

## 依赖

```bash
pip install -r requirements.txt
```

## 配置

在 `oj/oj` 里设置环境变量文件 `.env`, 指定使用的数据库, OJ公有账号等相关私密配置, 示例如下

```plaintext
SECRET_KEY=
# dev database
SQL_DEV_DB_NAME=
SQL_DEV_DB_USERNAME=
SQL_DEV_DB_PASSWORD=
# test database
SQL_TEST_DB_NAME=
SQL_TEST_DB_USERNAME=
SQL_TEST_DB_PASSWORD=
SQL_SERVER_HOST=
SQL_PORT=3306
# public account
HDU_ACCOUNT=
HDU_PASSWORD=
```

如有其它配置, 请在 `oj/oj/settings.py` 中进行修改

## 建立本地测评机

按照[评测机文档](https://github.com/QingdaoU/JudgeServer)指示建立 Docker image, 运行 JudgeServer 容器.

注意: 你需要正确配置好 `docker-compose.yml` 文件, 否则评测机服务不能正常运行.

```yml
volumes:
    - $PWD/tests/test_case:/test_case:ro
    - $PWD/log:/log
    # - $PWD/server:/code:ro
    - $PWD/run:/judger
environment:
    - BACKEND_URL=http://backend:80/api/judge_server_heartbeat
    - SERVICE_URL=http://judge-server:12358
    - TOKEN=YOUR_TOKEN_HERE
```

然后在 SWUFE-OJ 的配置中设定好

```env
JUDGE_SERVER_TOKEN=
JUDGE_SERVER_HOST=
JUDGE_SERVER_PORT=
JUDGE_SERVER_USER=
TEST_CASE_DIR=
JUDGE_SERVER_TEST_CASE_DIR=
```

同时配置好后端服务器和评测机服务器之间的 SSH 连接. 参考如下:

1. 评测机服务器生成 rsa 公私钥对

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

之后会让你设置密钥的名称(默认是 `id_rsa`), 以及 passphrase(SSH 连接的密码), 这里我们设置密码为空.

2. 评测机服务器将公钥 `id_rsa.pub` 拷贝到评测机服务器的 `authorized_keys` 文件中

```bash
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

3. 评测机服务器将密钥 `id_rsa` 拷贝到后端服务器的 `~/.ssh` 目录下, 并设置权限

```bash
chmod 600 ~/.ssh/id_rsa
```

4. 后端服务器添加评测机的 `known_hosts`

```bash
ssh-keyscan remote >> ~/.ssh/known_hosts
```

测试一下 `rsync` 是否正常工作

```bash
rsync -r README.md root@remote:/www/bar/
```

## 一些开发上的约束

- 按已有框架开发, 例如视图采用 CBV, Restful API
- 请[规范化提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/)
- Pull Request 需要经过**单元测试检验**以及 Code Review

生成 changelog 采用 eslint 格式

```bash
conventional-changelog -p eslint -i CHANGELOG.md -s
```

## 鸣谢

感谢下面的开源项目为 SWUFE-OJ 提供的参考

- [QDU OJ](https://github.com/QingdaoU/OnlineJudge)
- [HOJ](https://github.com/HimitZH/HOJ)

Developed by SingularityLab
