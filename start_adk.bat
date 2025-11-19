@echo off
REM Start ADK Web UI with GOOGLE_API_KEY loaded from .env.local

echo Loading environment variables from .env.local...

REM Read .env.local and set GOOGLE_API_KEY
for /f "tokens=1,2 delims==" %%a in ('findstr /r "^GOOGLE_API_KEY=" .env.local') do (
    set %%a=%%b
)

echo Starting ADK Web UI on port 8001...
echo API Key: %GOOGLE_API_KEY:~0,20%...

C:\Users\80133\AppData\Local\Programs\Python\Python314\Scripts\adk.exe web --port 8001

pause
