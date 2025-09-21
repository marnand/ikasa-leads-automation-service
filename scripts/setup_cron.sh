#!/bin/bash

# Script para configurar cron job da automação
# Execução: ./scripts/setup_cron.sh

PROJECT_PATH=$(pwd)
PYTHON_PATH="$PROJECT_PATH/venv/bin/python"
MAIN_SCRIPT="$PROJECT_PATH/src/main.py"

# Criar entrada do cron
CRON_ENTRY="0 8 * * 1-5 cd $PROJECT_PATH && $PYTHON_PATH $MAIN_SCRIPT >> logs/cron.log 2>&1"

echo "🔧 Configurando cron job para automação de leads..."

# Backup do crontab atual
crontab -l > /tmp/crontab_backup.txt 2>/dev/null || true

# Remover entradas antigas do projeto (se existirem)
crontab -l 2>/dev/null | grep -v "leads-automation" > /tmp/new_crontab.txt || true

# Adicionar nova entrada
echo "# Automação de Leads Contábeis - leads-automation" >> /tmp/new_crontab.txt
echo "$CRON_ENTRY" >> /tmp/new_crontab.txt

# Aplicar novo crontab
crontab /tmp/new_crontab.txt

# Verificar
echo "✅ Cron job configurado:"
echo "   • Execução: Segunda a sexta, 8:00"
echo "   • Comando: $CRON_ENTRY"
echo ""
echo "📋 Crontab atual:"
crontab -l | tail -5

# Limpeza
rm -f /tmp/new_crontab.txt