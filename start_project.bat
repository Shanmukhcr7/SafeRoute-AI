@echo off
echo ==============================================
echo 🚗 ROAD RISK AI - Enterprise Web Deployment
echo ==============================================
echo.

echo [1/2] Starting FastAPI Backend (Port 8000)...
start "Backend API" cmd /k "python -m uvicorn api.fastapi_app:app --reload"

echo [2/2] Starting React Vite Frontend (Port 5173)...
timeout /t 3 >nul
start "Frontend UI" cmd /k "cd web-ui && npm run dev"

echo.
echo ✅ System is successfully launching!
echo.
echo Dashboard URL: http://localhost:5173
echo REST API URL:  http://127.0.0.1:8000/docs
echo.
echo To stop the servers, close the two terminal windows that just opened.
pause
