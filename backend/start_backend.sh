#!/bin/bash
echo "🚀 Starting Fill.ai Backend Server..."
echo "📡 WebSocket server will run on http://localhost:5001"
echo "🔗 Frontend should connect to: ws://localhost:5001"
echo ""
echo "Make sure your .env file has the correct API keys!"
echo ""

source venv/bin/activate
python3 app.py
