# Docker 部署指南

## 环境要求

- 1核1G 以上云服务器
- Docker 20.10+ / Docker Compose 2.0+
- 开放 80 端口（HTTP）

## 快速开始

### 1. 安装 Docker

```bash
# 一键安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证
sudo docker --version
```

### 2. 上传项目

将 `mold-system-docker.zip` 上传到服务器任意目录，例如 `/opt/mold-system/`：

```bash
# 创建目录
sudo mkdir -p /opt/mold-system
cd /opt/mold-system

# 解压（用 scp/ftp 上传后解压）
unzip mold-system-docker.zip
```

解压后目录结构：
```
/opt/mold-system/
├── docker-compose.yml      # Docker 编排
├── Dockerfile              # Flask 后端镜像
├── deploy.sh               # 一键部署脚本
├── nginx/
│   └── nginx.conf          # Nginx 配置
├── backend/                # Flask 后端代码
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── requirements.txt
│   ├── routes/
│   ├── migrations/
│   └── dist/               # 前端构建产物
└── DOCKER_DEPLOY.md        # 本文件
```

### 3. 一键部署

```bash
cd /opt/mold-system
sudo bash deploy.sh
```

部署完成后访问：
```
http://你的服务器IP
```

默认账号：`admin` / 密码：`admin`

---

## 常用命令

```bash
# 查看运行状态
sudo docker-compose ps

# 查看日志
sudo docker-compose logs -f

# 查看后端日志
sudo docker-compose logs -f backend

# 重启服务
sudo docker-compose restart

# 停止服务
sudo docker-compose down

# 停止并删除数据（谨慎）
sudo docker-compose down -v
```

---

## 配置说明

### 数据库密码修改

编辑 `docker-compose.yml`，修改以下环境变量：

```yaml
mysql:
  environment:
    MYSQL_ROOT_PASSWORD: 你的新密码
    MYSQL_PASSWORD: 你的新密码

backend:
  environment:
    DB_PASSWORD: 你的新密码  # 与上面一致
```

修改后重新部署：
```bash
sudo docker-compose down
sudo docker-compose up -d
```

### 端口修改

如果 80 端口被占用，编辑 `docker-compose.yml`：

```yaml
nginx:
  ports:
    - "8080:80"   # 改为 8080 或其他端口
```

---

## 技术架构

```
用户请求
    |
    v
Nginx (端口 80)
    |-- 静态文件 (frontend/dist) --> 返回前端页面
    |-- /api/* --> 反向代理 --> Flask (端口 5000)
    |
MySQL (端口 3306)
    |
数据持久化 (Docker Volume)
```

- **Nginx**：服务前端静态文件 + 反向代理 API + SPA 路由支持
- **Flask**：处理业务逻辑和 API
- **MySQL**：数据持久化存储
- **前端**：React SPA，纯静态文件

所有数据（MySQL）通过 Docker Volume 持久化，重启容器不会丢失。
