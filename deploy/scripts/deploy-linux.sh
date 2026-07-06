#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "==> Build backend"
cd "$BACKEND_DIR"
mvn clean package -DskipTests

echo "==> Build frontend"
cd "$FRONTEND_DIR"
npm install
npm run build

echo "==> Install backend jar"
mkdir -p /opt/goods-admin/backend
cp "$BACKEND_DIR/target/goods-management-backend-1.0.0.jar" /opt/goods-admin/backend/app.jar

echo "==> Install frontend static files"
mkdir -p /usr/share/nginx/html/goods-admin
rm -rf /usr/share/nginx/html/goods-admin/*
cp -r "$FRONTEND_DIR/dist/"* /usr/share/nginx/html/goods-admin/

echo "==> Install service and nginx config"
cp "$PROJECT_ROOT/deploy/systemd/goods-admin-backend.service" /etc/systemd/system/goods-admin-backend.service
cp "$PROJECT_ROOT/deploy/nginx/goods-admin.conf" /etc/nginx/conf.d/goods-admin.conf

systemctl daemon-reload
systemctl enable goods-admin-backend
systemctl restart goods-admin-backend
nginx -t
systemctl reload nginx

echo "==> Deploy finished"

