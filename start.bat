@echo off
cd /d %~dp0
docker build -t ecoprimers .
docker run -p 5000:5000 ecoprimers