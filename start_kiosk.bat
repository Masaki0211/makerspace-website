@echo off
setlocal
title Makerspace Kiosk Launcher
REM ============================================================
REM  TTU Makerspace kiosk launcher
REM  Keep this file in the same folder as index.html.
REM ============================================================

cd /d "%~dp0"
echo Folder: %cd%

if not exist "index.html" (
  echo [ERROR] index.html is not in this folder. Put this .bat file next to index.html.
  goto :fail
)

REM ---- 1) Find Python ----
set "PY="
set "PYARG="
REM Ask PowerShell for the real python.exe path (works with pyenv, Anaconda, Store Python)
for /f "usebackq delims=" %%i in (`powershell -Command "try { python -c 'import sys; print(sys.executable)' } catch {}" 2^>nul`) do if exist "%%i" set "PY=%%i"
if not defined PY (python --version >nul 2>nul && set "PY=python")
if not defined PY (py -3 --version >nul 2>nul && set "PY=py" && set "PYARG=-3")
if not defined PY (
  echo [ERROR] Python was not found. Install it from python.org and check "Add python.exe to PATH".
  goto :fail
)
echo [OK] Python: "%PY%"

REM ---- 2) Make sure Ollama is running ----
where ollama >nul 2>nul
if errorlevel 1 (
  echo [WARN] Ollama is not installed. The assistant will use basic answers.
) else (
  tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul
  if errorlevel 1 (
    echo Starting Ollama...
    start "Ollama" /min ollama serve
  ) else (
    echo [OK] Ollama is running
  )
)

REM ---- 3) Start the web server on this computer only ----
echo Starting web server at http://localhost:8000 ...
start "Makerspace web server - keep this open" /min "%PY%" %PYARG% -m http.server 8000 --bind 127.0.0.1
timeout /t 4 /nobreak >nul

REM ---- 4) Find Chrome or Edge and open kiosk mode ----
set "BROWSER="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
) do if not defined BROWSER if exist %%P set "BROWSER=%%~P"

if defined BROWSER (
  echo [OK] Opening Chrome in kiosk mode. Press Alt+F4 to exit.
  start "" "%BROWSER%" --kiosk http://localhost:8000 --incognito --no-first-run
  goto :done
)

for %%P in (
  "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
  "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
) do if not defined BROWSER if exist %%P set "BROWSER=%%~P"

if defined BROWSER (
  echo [OK] Opening Edge in kiosk mode. Press Alt+F4 to exit.
  start "" "%BROWSER%" --kiosk http://localhost:8000 --edge-kiosk-type=fullscreen --no-first-run
  goto :done
)

echo [ERROR] Chrome or Edge was not found.
goto :fail

:done
echo.
echo Kiosk started. This window closes in 5 seconds.
timeout /t 5 >nul
exit /b 0

:fail
echo.
echo Something went wrong. Take a photo of this window and send it.
pause
exit /b 1
