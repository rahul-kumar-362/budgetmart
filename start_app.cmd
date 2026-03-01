@echo off
echo Starting BudgetMart Backend Server...
cd "%~dp0backend"
call "..\.venv\Scripts\activate.bat"
start "BudgetMart Backend" python app.py
echo.
echo Backend server has been started in a new window!
echo You can now refresh your frontend (index.html) search page.
pause
