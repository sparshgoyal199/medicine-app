@echo off
rem ------------------------------------------------------------
rem Start Regrowth OS backend (which also serves the frontend)
rem ------------------------------------------------------------

set "VENV_DIR=%~dp0\.venv"
set "UVICORN_EXE=%VENV_DIR%\Scripts\uvicorn.exe"

if not exist "%UVICORN_EXE%" (
    echo UVicorn executable not found in %VENV_DIR%\Scripts. Please ensure the virtual environment is installed.
    pause
    exit /b 1
)

rem Start the server in a new window
start "Regrowth OS Backend" "%UVICORN_EXE%" main:app --host 0.0.0.0 --port 8000 --reload

rem Give the server a moment to start
timeout /t 3 > nul

rem Open the app in the default browser
start http://localhost:8000

rem Keep this script window open so you can see any errors
echo Regrowth OS is running. Press any key to close this window.
pause
