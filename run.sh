#!/bin/bash

# 檢查是否有程式佔用 port 5050
PIDS=$(lsof -t -i :5050)

if [ -n "$PIDS" ]; then
  echo "Port 5050 is in use by PID(s): $PIDS"
  echo "Killing them..."
  kill -9 $PIDS
else
  echo "Port 5050 is free"
fi

# 啟動 Gunicorn
echo "Starting Gunicorn..."
gunicorn --workers 1 flask_app:app --bind 127.0.0.1:5050
