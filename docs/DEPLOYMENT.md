# 部署指南

本文档描述一种简单的非 Docker 部署方式，用于把 MarketMind Agent 发布为公开演示网站。

推荐目录结构：

```text
/opt/marketmind-agent/
  repo/
    backend/
    frontend/
  data/
    marketmind.db
```

推荐公开访问地址：

```text
Frontend: https://your-domain.com
Backend API: https://your-domain.com/api
Health:   https://your-domain.com/health
```

## 1. 服务器前置条件

需要安装：

- Python 3.11+
- Node.js 20+
- Nginx
- Git

Ubuntu 示例：

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx git
```

## 2. 克隆仓库

```bash
sudo mkdir -p /opt/marketmind-agent
sudo chown -R $USER:$USER /opt/marketmind-agent
cd /opt/marketmind-agent
git clone https://github.com/Q-maker521/MarketMind-agent.git repo
```

## 3. 后端配置

```bash
cd /opt/marketmind-agent/repo/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

创建真实环境配置文件：

```bash
cp .env.example .env
```

推荐生产环境配置：

```text
MARKETMIND_APP_ENV=production
MARKETMIND_CORS_ORIGINS=["https://your-domain.com"]
MARKETMIND_DATABASE_PATH=/opt/marketmind-agent/data/marketmind.db
MARKETMIND_MARKET_DATA_PROVIDER=mock
MARKETMIND_ALPHA_VANTAGE_API_KEY=
MARKETMIND_TWELVE_DATA_API_KEY=demo
MARKETMIND_LLM_PROVIDER=mock
MARKETMIND_LLM_API_BASE_URL=
MARKETMIND_LLM_API_KEY=
MARKETMIND_LLM_MODEL=
```

先手动启动一次：

```bash
cd /opt/marketmind-agent/repo/backend
. .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

检查健康状态：

```bash
curl http://127.0.0.1:8000/health
```

## 4. 后端 systemd 服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/marketmind-backend.service
```

服务内容：

```ini
[Unit]
Description=MarketMind Agent Backend
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/marketmind-agent/repo/backend
EnvironmentFile=/opt/marketmind-agent/repo/backend/.env
ExecStart=/opt/marketmind-agent/repo/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable marketmind-backend
sudo systemctl start marketmind-backend
sudo systemctl status marketmind-backend
```

查看日志：

```bash
journalctl -u marketmind-backend -f
```

## 5. 前端构建

创建前端环境文件：

```bash
cd /opt/marketmind-agent/repo/frontend
cp .env.example .env.production
```

设置：

```text
VITE_API_BASE_URL=https://your-domain.com
```

构建：

```bash
npm install
npm run build
```

静态文件输出目录：

```text
/opt/marketmind-agent/repo/frontend/dist
```

## 6. Nginx

创建站点配置：

```bash
sudo nano /etc/nginx/sites-available/marketmind-agent
```

示例配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /opt/marketmind-agent/repo/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/marketmind-agent /etc/nginx/sites-enabled/marketmind-agent
sudo nginx -t
sudo systemctl reload nginx
```

## 7. HTTPS

如果已经有域名，可以使用 Certbot 配置 HTTPS：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 8. 真实 Provider 配置

稳定公开演示模式：

```text
MARKETMIND_MARKET_DATA_PROVIDER=mock
MARKETMIND_LLM_PROVIDER=mock
```

真实行情数据测试：

Twelve Data demo key：

```text
MARKETMIND_MARKET_DATA_PROVIDER=twelve_data
MARKETMIND_TWELVE_DATA_API_KEY=demo
```

Alpha Vantage 行情数据：

```text
MARKETMIND_MARKET_DATA_PROVIDER=alpha_vantage
MARKETMIND_ALPHA_VANTAGE_API_KEY=your_key
```

真实 LLM 测试：

```text
MARKETMIND_LLM_PROVIDER=openai_compatible
MARKETMIND_LLM_API_BASE_URL=https://api.example.com/v1
MARKETMIND_LLM_API_KEY=your_key
MARKETMIND_LLM_MODEL=your_model
```

修改 `.env` 后重启后端：

```bash
sudo systemctl restart marketmind-backend
```

检查运行时能力：

```bash
curl https://your-domain.com/api/system/capabilities
```

## 9. 部署验收

运行：

```bash
curl https://your-domain.com/health
curl https://your-domain.com/api/system/capabilities
```

打开网站并确认：

- Workflow 模式可以创建任务
- 报告页签展示质量检查
- 链路页签展示所有节点
- 工具调用页签展示 provider 和本地工具
- 历史筛选可用
- 系统能力面板能反映 provider 配置

## 10. 更新部署

```bash
cd /opt/marketmind-agent/repo
git pull
cd backend
. .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart marketmind-backend
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```
