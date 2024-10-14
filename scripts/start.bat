@echo off

cd /d %~dp0
cd ..

call scripts/setup.bat
cls

python src/app.py %*