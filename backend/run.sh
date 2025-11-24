#!/bin/bash

# B4 Backend Run Script
# Starts the FastAPI backend with module system

echo "🚀 Starting B4 Backend..."
echo ""

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Must run from backend directory"
    echo "   cd /Users/ed/King/B4/backend && sh run.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

# Set environment variables for development
export ENVIRONMENT=development
export PORT=8080
export ENABLE_FIRESTORE_WRITES=False
export GEMINI_API_KEY="AIzaSyDHsFM9dLjuywFv5VTq0Li5fnJsuQviy2M"
# Add your DeepInfra API key here for gpt-oss-20b support
# export DEEPINFRA_API_KEY="your_deepinfra_api_key_here"

# Kill process on port 8080 if it exists
PID=$(lsof -ti :8080)
if [ -n "$PID" ]; then
    echo "⚠️  Killing existing process on port 8080 (PID: $PID)..."
    kill -9 $PID
    sleep 1 # Give it a moment to release the port
fi

echo ""
echo "✅ Starting server on http://localhost:8080"
echo ""
echo "Available endpoints:"
echo "  - http://localhost:8080/              (Service info)"
echo "  - http://localhost:8080/health        (Health check)"
echo "  - http://localhost:8080/api/modules/  (List modules)"
echo "  - http://localhost:8080/agents/       (List agents)"
echo "  - http://localhost:8080/docs          (API documentation)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the server using venv python explicitly
./venv/bin/python -m app.main
