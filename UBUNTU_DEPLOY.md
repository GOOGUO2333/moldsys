# Ubuntu 服务器从零部署教程

> 适用于：刚买的服务器，Ubuntu 20.04/22.04/24.04，什么都没装

---

## 第一步：连接你的服务器

### Windows 用户

1. 按 `Win + R`，输入 `cmd`，回车，打开黑色命令窗口
2. 输入以下命令（把 `你的服务器IP` 换成实际IP）：

```bash
ssh root@你的服务器IP
```

3. 第一次连接会提示，输入 `yes` 回车
4. 输入密码（输入时不会显示字符，这是正常的），回车

### Mac 用户

1. 打开"终端"（Terminal）应用
2. 执行同样的命令：

```bash
ssh root@你的服务器IP
```

> 连接成功后，你会看到类似 `root@ubuntu:~#` 的提示，表示已经登录到服务器

---

## 第二步：更新系统

连接上服务器后，依次执行以下命令（复制粘贴，每行执行完再执行下一行）：

```bash
# 更新软件源列表
apt update -y

# 升级已安装的软件
apt upgrade -y
```

> 这可能需要几分钟，看到提示符回来就是执行完了

---

## 第三步：安装 Docker

一条命令搞定：

```bash
curl -fsSL https://get.docker.com | sh
```

安装完成后，启动 Docker：

```bash
# 启动 Docker 服务
systemctl start docker

# 设置开机自启
systemctl enable docker

# 验证安装
 docker --version
```

> 应该输出类似 `Docker version 24.x.x`

---

## 第四步：安装 Docker Compose

```bash
# 下载 docker-compose
 curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
chmod +x /usr/local/bin/docker-compose

# 验证安装
 docker-compose --version
```

> 应该输出类似 `Docker Compose version v2.x.x`

---

## 第五步：上传项目文件

### 方法：用 scp 命令上传（推荐）

**不要关闭已经连接服务器的窗口，再打开一个新的命令窗口**（Windows 再开一个 cmd，Mac 再开一个终端）。

假设你下载的 `mold-system-docker.zip` 在电脑的 `下载` 文件夹里：

**Windows:**
```bash
cd %USERPROFILE%\Downloads
scp mold-system-docker.zip root@你的服务器IP:/opt/
```

**Mac:**
```bash
cd ~/Downloads
scp mold-system-docker.zip root@你的服务器IP:/opt/
```

> 会提示输入密码，输入服务器密码即可。上传需要几十秒。

---

## 第六步：在服务器上解压并部署

回到**第一个窗口**（已经 SSH 连接服务器的那个），执行：

```bash
# 进入 /opt 目录
cd /opt

# 安装 unzip（如果没有）
apt install -y unzip

# 解压
unzip mold-system-docker.zip

# 进入项目目录
cd mold-system-docker

# 查看文件（确认有 docker-compose.yml）
ls
```

---

## 第七步：一键部署

执行部署脚本：

```bash
bash deploy.sh
```

你会看到类似输出：
```
========================================
  模具模次管理系统 - Docker 部署
========================================
[1/5] 检查 Docker 环境...
[2/5] 拉取镜像并构建...
[3/5] 启动服务...
[4/5] 等待数据库初始化...
[5/5] 检查服务状态...
========================================
  部署完成!
========================================

访问地址: http://你的服务器IP

默认账号: admin
默认密码: admin
```

> 首次部署需要下载镜像，大概 3-5 分钟，耐心等待

---

## 第八步：访问系统

打开浏览器，输入：

```
http://你的服务器IP
```

看到登录页面就是成功了！

- 账号：`admin`
- 密码：`admin`

---

## 常用运维命令

```bash
# 查看服务运行状态
cd /opt/mold-system-docker && docker-compose ps

# 查看实时日志
cd /opt/mold-system-docker && docker-compose logs -f

# 重启服务
cd /opt/mold-system-docker && docker-compose restart

# 停止服务
cd /opt/mold-system-docker && docker-compose down

# 启动服务
cd /opt/mold-system-docker && docker-compose up -d
```

---

## 常见问题

### Q1: 访问不了？
检查服务器安全组/防火墙是否开放了 80 端口：
```bash
# 查看防火墙状态
ufw status

# 如果显示 active，添加 80 端口
ufw allow 80/tcp

# 云服务器还需要在控制台开放 80 端口（安全组）
```

### Q2: 部署脚本卡住？
可能是网络问题，手动执行：
```bash
cd /opt/mold-system-docker
docker-compose down 2>/dev/null
docker-compose pull
docker-compose build --no-cache
docker-compose up -d
sleep 10
docker-compose ps
```

### Q3: 如何修改数据库密码？
编辑 `docker-compose.yml` 文件，找到密码相关行修改，然后重新部署：
```bash
cd /opt/mold-system-docker
# 用 nano 编辑（Ctrl+O 保存，Ctrl+X 退出）
nano docker-compose.yml
# 修改后执行
docker-compose down
docker-compose up -d
```

### Q4: 数据会丢失吗？
不会。MySQL 数据存储在 Docker Volume 中，重启服务不会丢失。只有执行 `docker-compose down -v` 才会清除数据。

### Q5: 如何更新代码？
1. 下载新的 zip 包
2. 上传到服务器覆盖
3. 执行 `cd /opt/mold-system-docker && docker-compose restart`
