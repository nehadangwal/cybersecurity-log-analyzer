#!/bin/bash

echo "🛡️  Cybersecurity Log Analyzer - Setup Script"
echo "=============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "   You can edit it to add your OpenAI API key (optional)"
else
    echo "✅ .env file already exists"
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/uploads
mkdir -p tmp/uploads
echo "✅ Directories created"
echo ""

# Build and start services
echo "🐳 Building and starting Docker containers..."
echo "   This may take a few minutes on first run..."
echo ""

docker-compose up --build -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Application is running!"
    echo ""
    echo "📍 Access Points:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:5000/api"
    echo "   Database:  localhost:5432"
    echo ""
    echo "🔐 Login Credentials:"
    echo "   Username: admin"
    echo "   Password: password123"
    echo ""
    echo "📊 Test with sample logs:"
    echo "   example_logs/apache_sample.log"
    echo "   example_logs/zscaler_sample.log"
    echo ""
    echo "📖 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop:"
    echo "   docker-compose down"
    echo ""
    echo "Happy analyzing! 🎉"
else
    echo ""
    echo "❌ Something went wrong. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi
