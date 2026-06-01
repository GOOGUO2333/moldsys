#!/bin/bash
# 模具模次管理系统 - Docker 一键部署脚本

set -e

echo "========================================"
echo "  模具模次管理系统 - Docker 部署"
echo "========================================"

# Check Docker
echo ""
echo "[1/6] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    echo "请执行: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装"
    echo "请执行: apt install -y docker-compose-plugin"
    exit 1
fi

echo "      Docker: $(docker --version)"

# Determine compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi
echo "      Compose: $($COMPOSE_CMD version --short)"

# Check files
echo ""
echo "[2/6] 检查项目文件..."
for f in docker-compose.yml Dockerfile backend/dist/index.html backend/requirements.txt nginx/nginx.conf; do
    if [ ! -f "$f" ]; then
        echo "错误: 缺少文件 $f"
        exit 1
    fi
    echo "      OK: $f"
done

# Pull and build
echo ""
echo "[3/6] 拉取镜像并构建..."
$COMPOSE_CMD pull
$COMPOSE_CMD build --no-cache

# Start services
echo ""
echo "[4/6] 启动服务..."
$COMPOSE_CMD down 2>/dev/null || true
$COMPOSE_CMD up -d

# Wait for services
echo ""
echo "[5/6] 等待服务就绪（约15秒）..."
sleep 15

# Check status
echo ""
echo "[6/6] 检查服务状态..."
echo ""
$COMPOSE_CMD ps
echo ""

# Test API
echo "测试 API 连接..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health 2>/dev/null | grep -q "200"; then
    echo "      API 正常: /api/health 返回 200"
else
    echo "      警告: API 测试失败，查看日志: $COMPOSE_CMD logs backend"
fi

echo ""
echo "========================================"
echo "  部署完成!"
echo "========================================"
echo ""
echo "访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo '你的服务器IP')"
echo ""
echo "默认账号: admin"
echo "默认密码: admin"
echo ""
echo "排查命令:"
echo "  查看所有日志: $COMPOSE_CMD logs -f"
echo "  查看后端日志: $COMPOSE_CMD logs backend"
echo "  查看Nginx日志: $COMPOSE_CMD logs nginx"
echo "  重启服务:      $COMPOSE_CMD restart"
echo "  停止服务:      $COMPOSE_CMD down"
echo ""
