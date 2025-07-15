#!/bin/bash

echo "🤖 Setting up Confluence AI Agent..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python version $python_version is compatible"
else
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your credentials"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/custom_templates

# Initialize database
echo "🗄️ Initializing agent memory database..."
python3 -c "
from utils.ai_agent import ConfluenceAIAgent
agent = ConfluenceAIAgent(api_key='dummy')
print('✅ Database initialized')
"

echo "🎉 Setup complete!"
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python app.py"
echo "3. Open: http://localhost:5000"