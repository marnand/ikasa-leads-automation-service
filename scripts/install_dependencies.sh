#!/bin/bash

# Script para instalação de dependências
# Execução: ./scripts/install_dependencies.sh

echo "🔧 Instalando dependências do sistema de automação de leads..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION encontrado. Requer Python $REQUIRED_VERSION ou superior."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION encontrado"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📥 Instalando dependências Python..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p logs database config

# Verificar instalação
echo "🧪 Verificando instalação..."
python -c "
import sys
import aiohttp
import yaml
import loguru
import pydantic
print('✅ Todas as dependências instaladas com sucesso!')
print(f'✅ Python: {sys.version}')
"

echo ""
echo "🎉 Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure as APIs em config/settings.yaml"
echo "2. Execute: python src/main.py (para teste)"
echo "3. Configure cron job: ./scripts/setup_cron.sh"