#!/bin/bash

# =============================================================================
# Equipment Management Logistics - Quick Start Script
# =============================================================================

echo "🚀 Starting Equipment Management Logistics System..."

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
echo "🔧 Setting up environment variables..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
        echo "📝 Please edit .env file with your API keys and configuration"
    else
        echo "❌ .env.example not found. Please create .env file manually"
        exit 1
    fi
else
    echo "✅ .env file found"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ Failed to load environment variables"
    exit 1
fi

# =============================================================================
# PYTHON ENVIRONMENT
# =============================================================================
echo "🐍 Setting up Python environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# =============================================================================
# DATABASE SETUP
# =============================================================================
echo "🗄️  Setting up database..."

# Create database tables
python -c "
import sys
sys.path.insert(0, 'src')
from src.models.database import create_tables
create_tables()
print('✅ Database tables created successfully')
"

# =============================================================================
# FRONTEND SETUP
# =============================================================================
echo "🎨 Setting up React frontend..."

cd frontend

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

cd ..

# =============================================================================
# VALIDATION
# =============================================================================
echo "🔍 Validating configuration..."

# Check required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set (required for AI processing)"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set"
fi

# =============================================================================
# START SERVICES
# =============================================================================
echo "🚀 Starting services..."

# Start backend in background
echo "🔧 Starting backend server..."
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!

cd ..

# =============================================================================
# CLEANUP FUNCTION
# =============================================================================
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# =============================================================================
# STATUS
# =============================================================================
echo ""
echo "🎉 Equipment Management Logistics System is running!"
echo ""
echo "📋 Services:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Frontend Dashboard: http://localhost:3000"
echo ""
echo "📝 Next steps:"
echo "   1. Configure your API keys in .env file"
echo "   2. Upload delivery note photos via the frontend"
echo "   3. Monitor equipment movements and balances"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
