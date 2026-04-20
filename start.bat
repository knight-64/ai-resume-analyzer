@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM Quick Start Script for AI Resume Analyzer (Windows)

echo AI Resume Analyzer - Quick Start
echo.================================
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo Creating .env file...
    copy backend\.env.example backend\.env >nul
    echo PLEASE UPDATE backend\.env with your API key and LLM_PROVIDER
    pause
    exit /b 1
)

set "LLM_PROVIDER=claude"
set "ANTHROPIC_API_KEY="
set "GROQ_API_KEY="
set "PORT=8000"
set "RUN_PORT="

for /f "usebackq eol=# tokens=1,* delims==" %%A in ("backend\.env") do (
    set "KEY=%%A"
    set "VALUE=%%B"
    if /i "!KEY!"=="LLM_PROVIDER" set "LLM_PROVIDER=!VALUE!"
    if /i "!KEY!"=="ANTHROPIC_API_KEY" set "ANTHROPIC_API_KEY=!VALUE!"
    if /i "!KEY!"=="GROQ_API_KEY" set "GROQ_API_KEY=!VALUE!"
    if /i "!KEY!"=="PORT" set "PORT=!VALUE!"
)

if /i "!LLM_PROVIDER!"=="groq" (
    if "!GROQ_API_KEY!"=="" (
        echo ERROR: GROQ_API_KEY is missing in backend\.env while LLM_PROVIDER=groq
        pause
        exit /b 1
    )
    if /i "!GROQ_API_KEY!"=="your_groq_api_key_here" (
        echo ERROR: GROQ_API_KEY is still a placeholder in backend\.env
        pause
        exit /b 1
    )
) else (
    if "!ANTHROPIC_API_KEY!"=="" (
        echo ERROR: ANTHROPIC_API_KEY is missing in backend\.env while LLM_PROVIDER=!LLM_PROVIDER!
        pause
        exit /b 1
    )
    if /i "!ANTHROPIC_API_KEY!"=="your_api_key_here" (
        echo ERROR: ANTHROPIC_API_KEY is still a placeholder in backend\.env
        pause
        exit /b 1
    )
)

if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at backend\venv
    echo Create it with: python -m venv backend\venv
    pause
    exit /b 1
)

set "RUN_PORT=!PORT!"
call :is_port_in_use !RUN_PORT!
if !errorlevel! equ 0 (
    echo WARNING: Port !RUN_PORT! is already in use. Trying another port...
    for %%P in (8890 8891 8892 8893 8894 8895 8896 8897 8898 8899) do (
        call :is_port_in_use %%P
        if !errorlevel! neq 0 (
            set "RUN_PORT=%%P"
            goto :port_selected
        )
    )
    echo ERROR: No free fallback port found. Please stop the existing process and retry.
    pause
    exit /b 1
)

:port_selected
if not "!RUN_PORT!"=="!PORT!" (
    echo Using fallback port: !RUN_PORT!
)
set "PORT=!RUN_PORT!"

echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

echo Starting AI Resume Analyzer...
echo.================================
echo.
echo Server will be available at: http://localhost:!PORT!
echo Web UI: http://localhost:!PORT!
echo API Docs: http://localhost:!PORT!/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python run.py
exit /b %errorlevel%

:is_port_in_use
netstat -ano | findstr /R /C:":%~1 .*LISTENING" >nul
if %errorlevel% equ 0 (
    exit /b 0
)
exit /b 1
