#!/bin/bash

# =============================================================================
# Environment Setup Script for Equipment Management Logistics
# =============================================================================

echo "🔧 Setting up environment for Equipment Management Logistics..."

# =============================================================================
# CREATE .env FILE IF IT DOESN'T EXIST
# =============================================================================
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
    else
        echo "❌ .env.example not found. Please create .env file manually"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# =============================================================================
# GENERATE SECURE KEYS
# =============================================================================
echo "🔐 Generating secure keys..."

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets, string; alphabet = string.ascii_letters + string.digits + '-_'; print(''.join(secrets.choice(alphabet) for _ in range(32)))")

# Update .env file with generated secret key
if grep -q "SECRET_KEY=" .env; then
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    echo "✅ SECRET_KEY updated in .env"
else
    echo "SECRET_KEY=$SECRET_KEY" >> .env
    echo "✅ SECRET_KEY added to .env"
fi

# =============================================================================
# CREATE NECESSARY DIRECTORIES
# =============================================================================
echo "📁 Creating necessary directories..."

# Create uploads directory
mkdir -p uploads/logos
echo "✅ Created uploads directory"

# Create logs directory
mkdir -p logs
echo "✅ Created logs directory"

# =============================================================================
# VALIDATE ENVIRONMENT
# =============================================================================
echo "🔍 Validating environment configuration..."

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Please run setup.sh first"
else
    # Activate virtual environment and run validation
    source venv/bin/activate
    python validate_env.py
fi

# =============================================================================
# DISPLAY NEXT STEPS
# =============================================================================
echo ""
echo "🎉 Environment setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - ANTHROPIC_API_KEY (required for AI processing)"
echo "   - DATABASE_URL (if using PostgreSQL)"
echo "   - AWS credentials (optional, for image storage)"
echo ""
echo "2. Run validation:"
echo "   python validate_env.py"
echo ""
echo "3. Start the system:"
echo "   ./quick_start.bash"
echo ""
echo "📖 For detailed configuration, see ENVIRONMENT_SETUP.md"
