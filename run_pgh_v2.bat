@echo off
echo 🚀 Uruchamianie Polish Gig Hunter 2.0...
cd /d "C:\pppkkkooo"

REM Ustaw zmienne środowiskowe
set EMAIL_USER=lukasz.szemiot0330@gmail.com
set EMAIL_PASS=ylos uusz lmzh imda

REM Uruchom bota
python pgh_v2.py

echo ✅ Zakończono - %date% %time%
timeout /t 300 > nul
goto start
