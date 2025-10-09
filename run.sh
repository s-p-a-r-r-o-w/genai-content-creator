#!/bin/bash

# Generative AI Content Workflow - Quick Start Script

echo "🚀 Starting Generative AI Content Workflow"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OpenAI API key"
    echo "   Then run this script again"
    exit 1
fi

# Check if API key is set
if ! grep -q "OPENROUTER_API_KEY=" .env || grep -q "your_openrouter_api_key_here" .env; then
    echo "⚠️  OpenRouter API key not found in .env file"
    echo "📝 Please add your API key to .env file:"
    echo "   OPENROUTER_API_KEY=your_key_here"
    echo "   Then run this script again"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Streamlit app..."
echo "   App will open in your browser at: http://localhost:8501"
echo ""
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Start Streamlit app
streamlit run src/app.py