@echo off
rem Heleos Radar 24/7. Pon este archivo en la misma carpeta que heleos_radar.py y heleos_config.json.
rem Para que arranque solo al encender la laptop: Win+R, escribe shell:startup y copia ahi un acceso directo a este .bat.
cd /d "%~dp0"
title Heleos Radar
:otra
python heleos_radar.py --loop
echo El radar se detuvo. Reintentando en 60 segundos...
timeout /t 60 /nobreak >nul
goto otra
