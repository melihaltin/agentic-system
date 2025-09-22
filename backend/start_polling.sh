#!/bin/bash

# Start the polling service
echo "🚀 Starting Agent Integration Polling Service..."
echo "Press Ctrl+C to stop the service"
echo "========================================"

# Activate virtual environment if it exists
if [ -d "backend-env" ]; then
    source backend-env/bin/activate
    echo "✅ Activated virtual environment"
fi

# Run the polling service
python polling.py
