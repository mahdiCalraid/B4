#!/bin/bash

# Stop B4 Backend
echo "🛑 Stopping B4 Backend..."

# Kill any process on port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Server stopped"
else
    echo "✅ No server running on port 8080"
fi
