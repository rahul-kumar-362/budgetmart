@echo off
REM Starts the BudgetMart backend on http://127.0.0.1:5000
REM With no SERPAPI_KEY set, it runs in DEMO MODE with sample data.
echo Starting BudgetMart backend...
cd /d "%~dp0backend"
call "..\.venv\Scripts\activate.bat"
start "BudgetMart Backend" python run.py
echo.
echo Backend started in a new window on http://127.0.0.1:5000
echo Open frontend\index.html (or serve it) to use the app.
pause
