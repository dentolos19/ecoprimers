@echo off
cd /d %~dp0
docker build --tag ecoprimers .
docker run --rm --publish 5000:5000 --name ecoprimers ecoprimers