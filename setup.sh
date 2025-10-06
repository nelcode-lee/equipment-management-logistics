#!/bin/bash

# Equipment Tracking System Setup Script

echo "🚀 Setting up Equipment Tracking System..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+ and try again."
    exit 1
fi

echo "✅ Python 3 and Node.js are installed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys and database settings"
    echo "   Required: ANTHROPIC_API_KEY"
    echo "   Optional: DATABASE_URL, AWS credentials, Twilio credentials"
fi

# Setup frontend
echo "🎨 Setting up React frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

cd ..

# Create database tables
echo "🗄️  Setting up database..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.models.database import create_tables
create_tables()
print('✅ Database tables created successfully')
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - ANTHROPIC_API_KEY (required for AI processing)"
echo "   - DATABASE_URL (if using PostgreSQL)"
echo "   - AWS credentials (optional, for image storage)"
echo ""
echo "2. Start the backend:"
echo "   python main.py"
echo ""
echo "3. Start the frontend (in a new terminal):"
echo "   cd frontend && npm start"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "📖 See README.md for detailed documentation"

