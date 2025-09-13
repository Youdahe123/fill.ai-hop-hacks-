#!/bin/bash
echo "🌐 Starting Fill.ai Frontend Server..."
echo "📱 Frontend will run on http://localhost:3000"
echo "🔗 Make sure backend is running on http://localhost:5001"
echo ""

python3 -m http.server 3000
