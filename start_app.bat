@echo off
echo Starting Aspect-Based Product Recommender...

:: Start Backend
start "Backend Server" cmd /k "cd server & echo Installing requirements... & pip install -r requirements.txt & echo Starting Server... & python main.py"

:: Start Frontend
start "Frontend Client" cmd /k "cd client & echo Installing dependencies... & npm install & npm install axios & echo Starting Client... & npm run dev"

echo System starting... Access the UI at http://localhost:5173
pause
