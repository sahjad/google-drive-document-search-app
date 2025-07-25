#!/bin/bash

set -o allexport
source .env.config 2>/dev/null
set +o allexport


if [ ! -f "$CREDENTIALS_PATH" ]; then
  echo "ERROR: Credentials file not found at path: $CREDENTIALS_PATH"
  echo "Please check your .env.config file and ensure the credentials.json exists."
  exit 1
fi


echo "Activating virtual environment..."
source venv/bin/activate

echo "Checking if Elasticsearch is already running..."
if curl -s http://localhost:9200 >/dev/null; then
    echo "Elasticsearch is already running."
else
    echo "Starting Elasticsearch..."
    docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.10 >/dev/null 2>&1
    sleep 5
fi

echo "Starting ngrok..."
nohup ngrok http 8000 > ngrok.log 2>&1 &
sleep 5

echo "Fetching ngrok public URL..."
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url')
WEBHOOK_URL="$NGROK_URL/api/drive-webhook"
echo "Webhook URL: $WEBHOOK_URL"

echo "Updating .env with webhook URL..."
if grep -q "^WEBHOOK_URL=" .env; then
    sed -i.bak "s|^WEBHOOK_URL=.*|WEBHOOK_URL=$WEBHOOK_URL|" .env
else
    echo "WEBHOOK_URL=$WEBHOOK_URL" >> .env
fi

echo "Registering webhook..."
python scripts/register_drive_webhook.py

sleep 3

echo "Starting FastAPI server..."
uvicorn main:app --reload
