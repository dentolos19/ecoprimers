@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
set FLASK_APP=src/main.py
flask db migrate
flask db upgrade