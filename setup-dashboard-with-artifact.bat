@echo off
echo ========================================
echo Setting Up Dashboard with Latest Results
echo ========================================
echo.

REM Check if ai_analysis.json exists in Downloads or Temp
set "SOURCE_FILE="
if exist "%USERPROFILE%\Downloads\ai_analysis.json" (
    set "SOURCE_FILE=%USERPROFILE%\Downloads\ai_analysis.json"
    echo Found ai_analysis.json in Downloads
) else if exist "%USERPROFILE%\AppData\Local\Temp\*ai-analysis*\ai_analysis.json" (
    for /r "%USERPROFILE%\AppData\Local\Temp" %%f in (ai_analysis.json) do (
        set "SOURCE_FILE=%%f"
        echo Found ai_analysis.json in Temp
        goto :found
    )
)

:found
if "%SOURCE_FILE%"=="" (
    echo [ERROR] Could not find ai_analysis.json
    echo.
    echo Please:
    echo 1. Download 'ai-analysis' artifact from GitHub Actions
    echo 2. Extract the zip file
    echo 3. Note the location of ai_analysis.json
    echo 4. Run this command manually:
    echo    copy "path\to\ai_analysis.json" "%~dp0dashboard\public\data\ai_analysis.json"
    echo.
    pause
    exit /b 1
)

echo.
echo Copying AI analysis to dashboard...
mkdir "%~dp0dashboard\public\data" 2>nul
copy /Y "%SOURCE_FILE%" "%~dp0dashboard\public\data\ai_analysis.json"

if %ERRORLEVEL% EQU 0 (
    echo [OK] AI analysis copied successfully!
    echo.
    echo Starting dashboard...
    cd /d "%~dp0dashboard"
    
    REM Check if node_modules exists
    if not exist "node_modules" (
        echo Installing dependencies...
        call npm install
    )
    
    echo.
    echo ========================================
    echo Dashboard starting at http://localhost:5173
    echo ========================================
    echo.
    call npm run dev
) else (
    echo [ERROR] Failed to copy file
    echo Please copy manually:
    echo   From: %SOURCE_FILE%
    echo   To: %~dp0dashboard\public\data\ai_analysis.json
    pause
)
