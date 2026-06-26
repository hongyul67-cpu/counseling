@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 상담 일지 작성 도구

REM ── 최초 1회: 가상환경이 없으면 자동으로 만들고 패키지 설치 (인터넷 필요) ──
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo  [최초 1회 설정] 실행 환경을 준비합니다. 인터넷이 연결돼 있어야 합니다.
    echo  몇 분 걸릴 수 있으니 잠시만 기다려주세요...
    echo.
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    echo.
    echo  설정 완료!
)

echo.
echo  ────────────────────────────────────────────
echo   상담 일지 작성 도구를 시작합니다.
echo   잠시 후 브라우저가 자동으로 열립니다.
echo.
echo   종료하려면 이 검은 창을 닫거나 Ctrl+C 를 누르세요.
echo  ────────────────────────────────────────────
echo.

".venv\Scripts\python.exe" -m streamlit run app.py

echo.
echo  앱이 종료되었습니다. 아무 키나 누르면 창이 닫힙니다.
pause >nul
