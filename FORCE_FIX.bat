@echo off
echo ============================================
echo  FORCE FIX — Complete Cache Wipe
echo ============================================
cd /d "D:\Freelancing\MIS Portal\MIS_Portal"

:: Kill all python processes
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM python3.exe /T 2>nul
timeout /t 3 /nobreak >nul

:: Nuclear cache delete
echo Deleting ALL cache...
for /d /r "%cd%" %%d in (__pycache__) do rd /s /q "%%d" 2>nul
for /r "%cd%" %%f in (*.pyc) do del /f /q "%%f" 2>nul

:: Also clear streamlit cache
rmdir /s /q "%USERPROFILE%\.streamlit\cache" 2>nul
rmdir /s /q "%APPDATA%\streamlit" 2>nul

echo Done! Starting fresh...
echo.
python -m streamlit run app.py --server.runOnSave=false
