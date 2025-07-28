#!/bin/bash

echo "🏥 Checking ML Services Health..."

# Check if ML service is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ ML Services are running"
    
    # Test specific endpoints
    echo "🧪 Testing ML endpoints..."
    
    # Test teacher analytics
    curl -s -X POST http://localhost:8000/api/ml/teacher/attendance/analyze \
        -H "Content-Type: application/json" \
        -d '[]' > /dev/null && echo "✅ Teacher Analytics: OK" || echo "❌ Teacher Analytics: Failed"
    
    # Test parent analytics
    curl -s -X POST http://localhost:8000/api/ml/parent/sentiment/analyze \
        -H "Content-Type: application/json" \
        -d '{"messages": []}' > /dev/null && echo "✅ Parent Analytics: OK" || echo "❌ Parent Analytics: Failed"
    
else
    echo "❌ ML Services are not running"
    echo "💡 Start ML services with: ./start.sh"
fi 