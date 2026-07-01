# Deployment Guide

This guide describes a simple non-Docker deployment for a public demo website.

Recommended layout:

```text
/opt/marketmind-agent/
  repo/
    backend/
    frontend/
  data/
    marketmind.db
```

Recommended public URLs:

```text
Frontend: https://your-domain.com
Backend API: https://your-domain.com/api
Health:   https://your-domain.com/health
```

## 1. Server Prerequisites

Install:

- Python 3.11+
- Node.js 20+
- Nginx
- Git

Example on Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx git
```

## 2. Clone Repository

```bash
sudo mkdir -p /opt/marketmind-agent
sudo chown -R $USER:$USER /opt/marketmind-agent
cd /opt/marketmind-agent
git clone https://github.com/Q-maker521/MarketMind-agent.git repo
```

## 3. Backend Setup

```bash
cd /opt/marketmind-agent/repo/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Create a real backend environment file:

```bash
cp .env.example .env
```

Recommended production values:

```text
MARKETMIND_APP_ENV=production
MARKETMIND_CORS_ORIGINS=["https://your-domain.com"]
MARKETMIND_DATABASE_PATH=/opt/marketmind-agent/data/marketmind.db
MARKETMIND_MARKET_DATA_PROVIDER=mock
MARKETMIND_ALPHA_VANTAGE_API_KEY=
MARKETMIND_LLM_PROVIDER=mock
MARKETMIND_LLM_API_BASE_URL=
MARKETMIND_LLM_API_KEY=
MARKETMIND_LLM_MODEL=
```

Start once manually:

```bash
cd /opt/marketmind-agent/repo/backend
. .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Check:

```bash
curl http://127.0.0.1:8000/health
```

## 4. Backend systemd Service

Create:

```bash
sudo nano /etc/systemd/system/marketmind-backend.service
```

Service:

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

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable marketmind-backend
sudo systemctl start marketmind-backend
sudo systemctl status marketmind-backend
```

Logs:

```bash
journalctl -u marketmind-backend -f
```

## 5. Frontend Build

Create frontend environment file:

```bash
cd /opt/marketmind-agent/repo/frontend
cp .env.example .env.production
```

Set:

```text
VITE_API_BASE_URL=https://your-domain.com
```

Build:

```bash
npm install
npm run build
```

The static output is:

```text
/opt/marketmind-agent/repo/frontend/dist
```

## 6. Nginx

Create:

```bash
sudo nano /etc/nginx/sites-available/marketmind-agent
```

Example:

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

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/marketmind-agent /etc/nginx/sites-enabled/marketmind-agent
sudo nginx -t
sudo systemctl reload nginx
```

## 7. HTTPS

If you have a domain:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 8. Real Provider Configuration

Stable public demo:

```text
MARKETMIND_MARKET_DATA_PROVIDER=mock
MARKETMIND_LLM_PROVIDER=mock
```

Real market data trial:

No-key real market data:

```text
MARKETMIND_MARKET_DATA_PROVIDER=yahoo_finance
```

Alpha Vantage market data:

```text
MARKETMIND_MARKET_DATA_PROVIDER=alpha_vantage
MARKETMIND_ALPHA_VANTAGE_API_KEY=your_key
```

Real LLM trial:

```text
MARKETMIND_LLM_PROVIDER=openai_compatible
MARKETMIND_LLM_API_BASE_URL=https://api.example.com/v1
MARKETMIND_LLM_API_KEY=your_key
MARKETMIND_LLM_MODEL=your_model
```

After changing `.env`:

```bash
sudo systemctl restart marketmind-backend
```

Check runtime capabilities:

```bash
curl https://your-domain.com/api/system/capabilities
```

## 9. Deployment Verification

Run these checks:

```bash
curl https://your-domain.com/health
curl https://your-domain.com/api/system/capabilities
```

Open the website and verify:

- Workflow mode can create a task
- Report tab shows quality checks
- Trace tab shows all nodes
- Tool calls tab shows providers and local tools
- History filters work
- System capability panel reflects provider configuration

## 10. Update Deployment

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
