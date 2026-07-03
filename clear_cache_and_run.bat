@echo off
echo ============================================
echo  MIS Portal — Cache Clear + Restart
echo ============================================

cd /d "D:\Freelancing\MIS Portal\MIS_Portal"

echo.
echo [1/3] Stopping any running Streamlit...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] Clearing Python cache...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d"
        echo   Deleted: %%d
    )
)
del /s /q *.pyc 2>nul
echo   Cache cleared!

echo [3/3] Starting MIS Portal...
echo.
python -m streamlit run app.py

pause
