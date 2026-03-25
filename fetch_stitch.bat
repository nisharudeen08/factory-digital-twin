@echo off
REM Fetch Stitch Design Assets
REM Project ID: 8599590735454910619

set STITCH_API_KEY=%STITCH_API_KEY%
set PROJECT_ID=8599590735454910619
set OUTPUT_DIR=stitch_exports

echo ========================================
echo Fetching Stitch Design Assets
echo ========================================
echo.

if "%STITCH_API_KEY%"=="" (
    echo ERROR: STITCH_API_KEY environment variable not set!
    echo Please set it with: set STITCH_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

mkdir %OUTPUT_DIR% 2>nul

echo Screens to fetch:
echo 1. Setup: Machine Parameters (125bb32f3d594f649961f349939ba620)
echo 2. Home Dashboard (1c55ddfaa7674db282a56ce1a8398056)
echo 3. Bottleneck Alert (6faadc89bb024c3b81ac4c27653bed8a)
echo 4. Factory Type Selection (c86a79b1a0064bbd9d243e407b58e5f8)
echo 5. Simulate Screen (df21bebf755146d6a184d563ba25c38f)
echo.

REM Note: Replace these URLs with actual Stitch export URLs
REM Stitch typically provides export URLs like:
REM - PNG export: https://api.stitch.com/v1/projects/{PROJECT_ID}/screens/{SCREEN_ID}/export.png
REM - Code export: https://api.stitch.com/v1/projects/{PROJECT_ID}/screens/{SCREEN_ID}/export.xml

echo To fetch your Stitch designs, you need to:
echo 1. Open Stitch and go to your project
echo 2. Click Export on each screen
echo 3. Copy the export URLs
echo 4. Replace the URLs below with your actual export URLs
echo.

REM Example commands (replace URLs with your actual Stitch export URLs):
REM curl -L -H "Authorization: Bearer %STITCH_API_KEY%" -o "%OUTPUT_DIR%/setup_machine_params.png" "https://api.stitch.com/v1/projects/%PROJECT_ID%/screens/125bb32f3d594f649961f349939ba620/export.png"
REM curl -L -H "Authorization: Bearer %STITCH_API_KEY%" -o "%OUTPUT_DIR%/home_dashboard.png" "https://api.stitch.com/v1/projects/%PROJECT_ID%/screens/1c55ddfaa7674db282a56ce1a8398056/export.png"
REM curl -L -H "Authorization: Bearer %STITCH_API_KEY%" -o "%OUTPUT_DIR%/bottleneck_alert.png" "https://api.stitch.com/v1/projects/%PROJECT_ID%/screens/6faadc89bb024c3b81ac4c27653bed8a/export.png"
REM curl -L -H "Authorization: Bearer %STITCH_API_KEY%" -o "%OUTPUT_DIR%/factory_type.png" "https://api.stitch.com/v1/projects/%PROJECT_ID%/screens/c86a79b1a0064bbd9d243e407b58e5f8/export.png"
REM curl -L -H "Authorization: Bearer %STITCH_API_KEY%" -o "%OUTPUT_DIR%/simulate_screen.png" "https://api.stitch.com/v1/projects/%PROJECT_ID%/screens/df21bebf755146d6a184d563ba25c38f/export.png"

echo.
echo Done! Check the '%OUTPUT_DIR%' folder for exported assets.
pause
