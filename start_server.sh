#!/bin/bash

# 进入项目目录
cd "$(dirname "$0")"

if [ -d "~/guessr/bin" ]; then
    source ~/guessr/bin/activate
elif [ -d "/home/$(whoami)/guessr/bin" ]; then
    source /home/$(whoami)/guessr/bin/activate
fi

# 使用gunicorn启动服务
echo "Starting server with Eventlet worker..."
export PYTHONUNBUFFERED=1
gunicorn --worker-class eventlet -w 3 -b 0.0.0.0:12920 app:app
