# Acckio 自动签到脚本

基于 Selenium 的 acck.io 自动签到工具，支持 Docker 部署和定时任务。

## 功能特性

- ✅ 自动登录并签到 acck.io
- ✅ Server酱推送通知（可选）
- ✅ Docker 容器化部署

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/nianzhibai/Acckio-checkin.git
cd Acckio-checkin
```

### 2. 配置账号信息

编辑 `config.ini`，填入你的信息：

```ini
[Account]
# 你的 Acckio 邮箱
email = your_email@example.com
# 你的 Acckio 密码
password = your_password
# Server酱推送密钥（可选，不需要通知可以留空）
push_key = 

[Others]
# 每个操作之间的等待时间（秒），网络较慢时可以适当增加
sleep_time = 3
```

### 3. 构建 Docker 镜像

```bash
docker build -t acck-checkin .
```

### 4. 运行签到

```bash
docker run --rm -v $(pwd):/app acck-checkin
```

## 设置定时任务

### 方法1：使用 Crontab（推荐）

编辑 crontab：
```bash
crontab -e
```

添加定时任务（根据需要选择一个）：

```bash
# 每天早上 8 点执行
0 8 * * * cd /root/Acckio-checkin && docker run --rm -v $(pwd):/app acck-checkin
```

**注意**：将 `/root/Acckio-checkin` 替换为你的实际项目路径。

查看已设置的定时任务：
```bash
crontab -l
```

### 方法2：手动执行

```bash
cd /root/Acckio-checkin
docker run --rm -v $(pwd):/app acck-checkin
```

## 查看日志

签到日志会保存在 `acckio.log` 文件中：

```bash
cat acckio.log
```

## Server酱推送配置（可选）

如果需要接收签到通知，可以配置 Server酱：

1. 访问 [Server酱官网](https://sct.ftqq.com/) 注册账号
2. 获取你的 SendKey（推送密钥）
3. 在 `config.ini` 中填入 `push_key`

推送消息示例：
```
标题：Acck.io签到
内容：
2026-02-05 08:00:00
通过登录凭证登录成功
签到成功, 获得了5个积分，当前总积分：172
```

## 文件说明

```
Acckio-checkin/
├── Dockerfile              # Docker 镜像构建文件
├── requirements.txt        # Python 依赖包列表
├── acckio.py               # 主程序脚本
├── config.ini              # 配置文件
├── auth_data.json          # 登录凭证（第一次执行脚本并成功登录后会生成）
└── acckio.log              # 运行日志（第一次执行脚本后会生成）
```


## 更新日志

### v1.0.0 (2026-02-05)
- 初始版本发布
- 支持自动登录和签到
- 支持 Docker 部署
- 支持 Server酱推送通知

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请在 GitHub 上提交 Issue。

---

⭐ 如果这个项目对你有帮助，欢迎 Star！
