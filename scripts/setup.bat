@echo off

cd /d %~dp0
cd ..

echo Setting up virtual environment...

if not exist ".venv" (
    py -m venv ".venv"
)

call .venv\Scripts\activate.bat
pip install -r "requirements.txt" >nul