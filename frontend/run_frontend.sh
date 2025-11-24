#!/bin/bash

# Define the port
PORT=5174

echo "Cleaning up port $PORT..."

# Find and kill process on the port
PID=$(lsof -ti:$PORT)
if [ -n "$PID" ]; then
  echo "Killing process $PID on port $PORT"
  kill -9 $PID
else
  echo "No process found on port $PORT"
fi

# Run the frontend
echo "Starting frontend on port $PORT..."
npm run dev -- --port $PORT --host
