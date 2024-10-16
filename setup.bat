@echo off
cd /d %~dp0

echo Setting up virtual environment...
if not exist ".venv" (
    py -m venv ".venv"
)
call .venv\Scripts\activate.bat

echo Checking requirements...
pip install -r "requirements.txt" >nul