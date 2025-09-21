#!/bin/bash

# Script para executar o container Docker

echo "🐳 Construindo imagem Docker..."
docker-compose build

echo "🚀 Iniciando container..."
docker-compose up -d

echo "📋 Status dos containers:"
docker-compose ps

echo "📝 Para ver os logs em tempo real:"
echo "docker-compose logs -f ikasa-leads-automation"

echo "🛑 Para parar o container:"
echo "docker-compose down"