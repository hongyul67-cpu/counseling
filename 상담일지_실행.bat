@echo off
cd /d "%~dp0"
title Counseling Log Tool

REM --- Skip Streamlit first-run email prompt ---
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
    > "%USERPROFILE%\.streamlit\credentials.toml" echo [general]
    >> "%USERPROFILE%\.streamlit\credentials.toml" echo email = ""
)

REM --- First run: create venv and install packages (internet required) ---
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo  [First-time setup] Preparing the environment. Internet required.
    echo  This may take a few minutes. Please wait...
    echo.
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    echo.
    echo  Setup complete!
)

echo.
echo  ============================================
echo    Starting Counseling Log Tool...
echo    Your browser will open automatically.
echo.
echo    To stop: close this window or press Ctrl+C
echo  ============================================
echo.

".venv\Scripts\python.exe" -m streamlit run app.py

echo.
echo  App stopped. Press any key to close this window.
pause >nul
