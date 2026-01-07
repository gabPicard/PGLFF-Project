@echo off

echo ================================================
echo Daily Report Windows Task Scheduler Setup
echo ================================================
echo.

REM Get the project directory
set "PROJECT_DIR=%~dp0.."
pushd "%PROJECT_DIR%"
set "PROJECT_DIR=%CD%"
popd

echo Project directory: %PROJECT_DIR%
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Get Python path
for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i
echo Python path: %PYTHON_PATH%
echo.

REM Create directories if they don't exist
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"
if not exist "%PROJECT_DIR%\reports" mkdir "%PROJECT_DIR%\reports"

echo Testing report generation script...
"%PYTHON_PATH%" "%PROJECT_DIR%\scripts\generate_daily_report.py"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Report script test failed
    echo Please check that all dependencies are installed: pip install -r requirements.txt
    exit /b 1
)

echo.
echo ================================================
echo Creating Scheduled Task
echo ================================================
echo.
echo The task will run daily at 8:00 PM (20:00)
echo.

REM Remove existing task if it exists
schtasks /query /tn "DailyPortfolioReport" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Removing existing task...
    schtasks /delete /tn "DailyPortfolioReport" /f
)

REM Create the scheduled task
REM Run daily at 8:00 PM
schtasks /create ^
    /tn "DailyPortfolioReport" ^
    /tr "\"%PYTHON_PATH%\" \"%PROJECT_DIR%\scripts\generate_daily_report.py\" >> \"%PROJECT_DIR%\logs\cron_daily_report.log\" 2>&1" ^
    /sc daily ^
    /st 20:00 ^
    /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Task created successfully!
    echo.
) else (
    echo.
    echo Error creating task. You may need to run this script as Administrator.
    exit /b 1
)

echo ================================================
echo Verification
echo ================================================
schtasks /query /tn "DailyPortfolioReport" /fo LIST /v

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo The daily report will be generated at 8:00 PM every day.
echo.
echo Useful commands:
echo   - View task:          schtasks /query /tn "DailyPortfolioReport" /fo LIST /v
echo   - Run task now:       schtasks /run /tn "DailyPortfolioReport"
echo   - Delete task:        schtasks /delete /tn "DailyPortfolioReport" /f
echo   - View logs:          type "%PROJECT_DIR%\logs\cron_daily_report.log"
echo   - View reports:       dir "%PROJECT_DIR%\reports"
echo   - Test script:        python "%PROJECT_DIR%\scripts\generate_daily_report.py"
echo.
pause
