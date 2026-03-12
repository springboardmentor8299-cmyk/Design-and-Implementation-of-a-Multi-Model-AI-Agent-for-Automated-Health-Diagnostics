@echo off
echo ========================================
echo AI Health Diagnostic Agent
echo ========================================
echo.
echo Choose an option:
echo 1. Run Flask Web App
echo 2. Run Streamlit App (with AI)
echo 3. Install Dependencies
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting Flask app...
    cd Design-and-Implementation-of-a-Multi-Model-AI-Agent-for-Automated-Health-Diagnostics
    python app.py
) else if "%choice%"=="2" (
    echo Starting Streamlit app...
    streamlit run Agent.py
) else if "%choice%"=="3" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
    echo Installation complete!
    pause
) else if "%choice%"=="4" (
    exit
) else (
    echo Invalid choice!
    pause
)
