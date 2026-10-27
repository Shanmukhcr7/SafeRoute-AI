@echo off
echo ==============================================
echo 🚗 SAFEROUTE-AI - Modern Full-Stack Suite
echo ==============================================
echo.

echo [1/2] Starting FastAPI Backend (Port 8000)...
start "SafeRoute-AI Backend" cmd /k "python -m uvicorn api.fastapi_app:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting React Modern UI (Port 5173)...
timeout /t 2 >nul
start "SafeRoute-AI React UI" cmd /k "npm --prefix web-ui run dev"

echo.
echo ✅ SafeRoute-AI Full-Stack is running!
echo.
echo 🌐 Modern React Dashboard: http://localhost:5173
echo ⚡ FastAPI Swagger Docs:    http://127.0.0.1:8000/docs
echo.
echo (Streamlit legacy dashboard still available via: streamlit run dashboard/app.py)
echo.
echo To stop the servers, close the opened terminal windows.
pause
