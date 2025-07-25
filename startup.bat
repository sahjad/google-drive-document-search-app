@echo off

echo Activating virtual environment...
call venv\Scripts\activate.bat


echo Checking if Elasticsearch is already running...
powershell -Command "try { $response = Invoke-WebRequest -Uri http://localhost:9200 -UseBasicParsing -TimeoutSec 3; exit 0 } catch { exit 1 }"
if %errorlevel%==0 (
    echo Elasticsearch is already running.
) else (
    echo Starting Elasticsearch...
    docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.10 >nul 2>&1
    timeout /t 5 >nul
)

timeout /t 5 >nul

echo Starting ngrok...
start cmd /k "ngrok http 8000 --log=stdout > ngrok.log"

timeout /t 5 >nul

for /f "tokens=*" %%i in ('powershell -Command "(Invoke-RestMethod http://127.0.0.1:4040/api/tunnels).tunnels | Where-Object {$_.proto -eq 'https'} | Select-Object -ExpandProperty public_url"') do (
    set "NGROK_URL=%%i"
)

set "WEBHOOK_URL=%NGROK_URL%/api/drive-webhook"

echo Updating .env with webhook URL: %WEBHOOK_URL%
powershell -Command "(Get-Content .env) -replace 'WEBHOOK_URL=.*', 'WEBHOOK_URL=%WEBHOOK_URL%' | Set-Content .env"

echo Registering webhook...
python scripts/register_drive_webhook.py

timeout /t 5 >nul

echo Starting FastAPI server...
start cmd /k "uvicorn main:app --reload"

echo All services started!
exit
