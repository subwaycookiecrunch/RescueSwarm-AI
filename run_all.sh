#!/bin/bash
set -e

echo "=========================================================="
echo " Starting RescueSwarm AI — Autonomous Crisis Command Grid "
echo "=========================================================="

# Trap to kill background jobs on exit
trap 'kill 0' EXIT

# Start backend
echo "[1/2] Launching FastAPI backend on http://127.0.0.1:8000..."
./venv/bin/python -m uvicorn rescueswarm.api:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 1.5

# Start frontend
echo "[2/2] Launching Vite Frontend on http://localhost:5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo " RescueSwarm is Live!"
echo " Command Center: http://localhost:5173"
echo " API Docs:       http://127.0.0.1:8000/docs"
echo " Press Ctrl+C to shut down all processes."
echo "=========================================================="

wait
