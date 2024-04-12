# SWUFE-OJ 后端

技术栈: Python3.12 + Django 4.2 + MySQL 8.0.21 + Redis + Docker

在线文档: [gitbook](https://singularity-backend.gitbook.io/backend-online-doc/swufe-oj/readme)

主要 features:

- 前后端分离项目
- 支持虚拟远程评测(vjudge), 包括 HDU, Codeforces 等主流平台
- 题解/讨论区

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

## 一些开发上的约束

- 按已有框架开发, 例如视图采用 CBV, Restful API
- 请[规范化提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/)
- Pull Request 需要经过单元测试检验

生成 changelog 采用 eslint 格式

```bash
conventional-changelog -p eslint -i CHANGELOG.md -s
```

## 鸣谢

感谢下面的开源项目为 SWUFE-OJ 提供的参考

- [QDU OJ](https://github.com/QingdaoU/OnlineJudge)
- [HOJ](https://github.com/HimitZH/HOJ)
