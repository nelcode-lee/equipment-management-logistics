#!/bin/bash

# Equipment Management Logistics - Backend Startup Script
# This script starts the backend API with all required environment variables loaded

cd /Users/admin/equipment_management_logistics

# Load environment variables from .env file
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000,https://equipment-office-dashboard.vercel.app,https://equipment-driver-app.vercel.app"
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d'=' -f2)

echo "🚀 Starting Equipment Management API..."
echo "✅ CORS Origins: $CORS_ORIGINS"
echo "✅ ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:20}..."

# Activate virtual environment and start server
source venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
