@echo off
setlocal
echo.
echo  ==========================================
echo   Defender Fraud Detection Dashboard
echo  ==========================================
echo.

set SCRIPTS=C:\Users\yerke\AppData\Local\Programs\Python\Python311\Scripts

echo [1/3] Installing dependencies...
py -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Check your Python installation.
    pause
    exit /b 1
)

echo.
echo [2/3] Training ML models (this may take a few minutes)...
py backend\models\train.py
if errorlevel 1 (
    echo WARNING: Training script reported an error. Check output above.
    pause
)

echo.
echo [3/3] Launching Streamlit Dashboard...
echo  Open your browser at: http://localhost:8501
echo.
py -m streamlit run streamlit_app.py --server.headless false

pause
