@echo off
echo ===================================
echo  Starting Regrowth OS Frontend
echo ===================================
cd /d "%~dp0frontend"
echo Frontend running at: http://localhost:3000
echo Open your browser and go to: http://localhost:3000
python -m http.server 3000
pause
