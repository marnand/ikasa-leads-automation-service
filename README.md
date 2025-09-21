# 🤖 Sistema de Automação de Captação de Leads Contábeis

## 📋 Visão Geral

Sistema Python para automação completa de captação de leads de empresas recém-criadas, integrando **CNPJá** → **4C CRM** → **G-Click** com execução via cron jobs.

## 🎯 Objetivos

- ✅ Automatizar busca diária de empresas criadas (CNPJá API)
- ✅ Evitar duplicados com persistência local
- ✅ Cadastrar leads automaticamente no 4C CRM
- ✅ Disparar e-mails de contato via G-Click
- ✅ Logs detalhados e controle de execução
- ✅ Execução programada via cron jobs

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cron Job      │────│  Python Service  │────│   SQLite DB     │
│   (Scheduler)   │    │   (Orquestrador) │    │  (Duplicados)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────▼───┐ ┌─────▼─────┐ ┌──▼────────┐
            │  CNPJá API │ │ 4C CRM API│ │G-Click API│
            │(Empresas) │ │  (Leads)  │ │ (E-mails) │
            └───────────┘ └───────────┘ └───────────┘
```

## 📂 Estrutura do Projeto

```
leads-automation/
│
├── 📁 src/
│   ├── 📄 main.py                 # Ponto de entrada principal
│   ├── 📁 services/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 cnpja_service.py     # Integração CNPJá API
│   │   ├── 📄 crm_service.py      # Integração 4C CRM API
│   │   └── 📄 gclick_service.py   # Integração G-Click API
│   ├── 📁 models/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 company.py          # Modelo empresa
│   │   └── 📄 lead.py             # Modelo lead
│   ├── 📁 database/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 connection.py       # Conexão SQLite
│   │   └── 📄 repository.py       # Operações banco de dados
│   └── 📁 utils/
│       ├── 📄 __init__.py
│       ├── 📄 logger.py           # Sistema de logs
│       ├── 📄 config.py           # Configurações
│       └── 📄 validators.py       # Validações
│
├── 📁 config/
│   └── 📄 settings.yaml           # Configurações do sistema
│
├── 📁 logs/                       # Logs de execução
│   └── 📄 automation.log
│
├── 📁 database/
│   └── 📄 leads.db                # Base SQLite
│
├── 📁 scripts/
│   ├── 📄 setup_cron.sh           # Configuração cron job
│   └── 📄 install_dependencies.sh # Instalação dependências
│
├── 📁 tests/                      # Testes unitários
│   ├── 📄 test_services.py
│   └── 📄 test_database.py
│
├── 📄 requirements.txt            # Dependências Python
├── 📄 docker-compose.yml          # Container (opcional)
├── 📄 Dockerfile                  # Imagem Docker
└── 📄 README.md                   # Documentação
```

## ⚙️ Instalação e Configuração

### 1. Pré-requisitos

```bash
# Python 3.8+
python --version

# Git
git --version

# Cron (Linux/macOS)
crontab -l
```

### 2. Clonagem e Setup

```bash
# Clone do repositório
git clone https://github.com/seu-usuario/leads-automation.git
cd leads-automation

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Tornar scripts executáveis
chmod +x scripts/*.sh
```

### 3. Configuração das APIs

Edite o arquivo `config/settings.yaml`:

```yaml
apis:
  cnpja:
    base_url: "https://api.cnpja.com.br"
    token: "SEU_TOKEN_CNPJA"
    timeout: 30
    
  crm_4c:
    base_url: "https://api.4c.com.br"
    api_key: "SUA_API_KEY_4C"
    timeout: 30
    
  gclick:
    base_url: "https://api.gclick.com.br"
    token: "SEU_TOKEN_GCLICK"
    timeout: 30

database:
  type: "sqlite"
  path: "database/leads.db"

logging:
  level: "INFO"
  file: "logs/automation.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5

scheduler:
  run_hour: "08"      # Executar às 8h
  run_minute: "00"    # Aos 00 minutos
```

### 4. Inicializar Banco de Dados

```bash
# Executar script de inicialização
python src/database/__init__.py
```

## 🚀 Implementação dos Componentes

### 1. Serviço Principal (`src/main.py`)

```python
#!/usr/bin/env python3
"""
Sistema de Automação de Captação de Leads Contábeis
Execução: python src/main.py
"""

import sys
import asyncio
from datetime import datetime, timedelta
from src.services.cnpja_service import CNPJAService
from src.services.crm_service import CRMService
from src.services.gclick_service import GClickService
from src.database.repository import LeadRepository
from src.utils.logger import setup_logger
from src.utils.config import load_config

async def main():
    """Função principal de execução"""
    
    # Setup
    config = load_config()
    logger = setup_logger()
    
    try:
        logger.info("🚀 Iniciando automação de leads...")
        
        # Instanciar serviços
        cnpja = CNPJAService(config)
        crm = CRMService(config)
        gclick = GClickService(config)
        db = LeadRepository(config)
        
        # Data de busca (ontem)
        yesterday = datetime.now() - timedelta(days=1)
        search_date = yesterday.strftime("%Y-%m-%d")
        
        logger.info(f"📅 Buscando empresas criadas em: {search_date}")
        
        # 1. Buscar empresas no CNPJá
        companies = await cnpja.get_companies_by_date(search_date)
        logger.info(f"🏢 Encontradas {len(companies)} empresas")
        
        if not companies:
            logger.info("❌ Nenhuma empresa encontrada para hoje")
            return
        
        leads_processed = 0
        leads_duplicated = 0
        leads_failed = 0
        
        # 2. Processar cada empresa
        for company in companies:
            try:
                # Verificar duplicados
                if db.lead_exists(company.cnpj):
                    leads_duplicated += 1
                    logger.debug(f"⚠️  Lead duplicado ignorado: {company.cnpj}")
                    continue
                
                # Cadastrar no CRM
                lead_id = await crm.create_lead(company)
                logger.info(f"✅ Lead criado no CRM: {lead_id}")
                
                # Disparar e-mail
                email_sent = await gclick.send_email(company)
                
                if email_sent:
                    logger.info(f"📧 E-mail enviado para: {company.email}")
                else:
                    logger.warning(f"⚠️  Falha no envio de e-mail: {company.email}")
                
                # Salvar no banco local
                db.save_lead(company, lead_id)
                leads_processed += 1
                
            except Exception as e:
                leads_failed += 1
                logger.error(f"❌ Erro ao processar {company.cnpj}: {str(e)}")
        
        # Relatório final
        logger.info("📊 RELATÓRIO DE EXECUÇÃO:")
        logger.info(f"   • Leads processados: {leads_processed}")
        logger.info(f"   • Leads duplicados: {leads_duplicated}")
        logger.info(f"   • Leads com falha: {leads_failed}")
        logger.info("✅ Automação concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"💥 Erro crítico na automação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Configuração Cron Job (`scripts/setup_cron.sh`)

```bash
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
```

### 3. Modelos de Dados (`src/models/company.py`)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Company:
    """Modelo para dados da empresa"""
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str]
    email: Optional[str]
    telefone: Optional[str]
    endereco: Optional[str]
    cidade: str
    estado: str
    cep: Optional[str]
    data_abertura: datetime
    atividade_principal: str
    situacao: str
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        self.cnpj = self.clean_cnpj(self.cnpj)
        
    @staticmethod
    def clean_cnpj(cnpj: str) -> str:
        """Remove formatação do CNPJ"""
        return ''.join(filter(str.isdigit, cnpj))
    
    @property
    def formatted_cnpj(self) -> str:
        """CNPJ formatado"""
        cnpj = self.cnpj.zfill(14)
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'cnpj': self.cnpj,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'data_abertura': self.data_abertura.isoformat(),
            'atividade_principal': self.atividade_principal,
            'situacao': self.situacao
        }
```

## 🔧 Dependências (`requirements.txt`)

```txt
# Framework web e HTTP
aiohttp==3.9.1
requests==2.31.0

# Banco de dados
sqlite3

# Configuração e YAML
PyYAML==6.0.1
python-decouple==3.8

# Logs e utilitários
loguru==0.7.2
python-dateutil==2.8.2

# Validação de dados
pydantic==2.5.2

# Testes
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0

# Monitoramento (opcional)
psutil==5.9.6

# Formatação e linting (dev)
black==23.11.0
flake8==6.1.0
```

## 🐳 Docker (Opcional)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Configurar permissões
RUN chmod +x scripts/*.sh

# Configurar cron
RUN ./scripts/setup_cron.sh

# Comando padrão
CMD ["cron", "-f"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  leads-automation:
    build: .
    container_name: leads-automation
    volumes:
      - ./logs:/app/logs
      - ./database:/app/database
      - ./config:/app/config
    environment:
      - TZ=America/Sao_Paulo
    restart: unless-stopped
```

## 📊 Monitoramento e Logs

### 1. Verificar Status

```bash
# Verificar logs em tempo real
tail -f logs/automation.log

# Verificar execuções do cron
tail -f logs/cron.log

# Status do cron job
crontab -l | grep leads
```

### 2. Relatórios Diários

```bash
# Script de relatório diário
./scripts/daily_report.sh
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest tests/

# Testes com cobertura
pytest --cov=src tests/

# Teste manual de execução
python src/main.py --test-mode
```

## 🚀 Deploy em Produção

### 1. Servidor Linux (Ubuntu/CentOS)

```bash
# 1. Clonar e configurar projeto
git clone <repo-url>
cd leads-automation

# 2. Instalar dependências
./scripts/install_dependencies.sh

# 3. Configurar APIs
nano config/settings.yaml

# 4. Configurar cron
./scripts/setup_cron.sh

# 5. Testar execução
python src/main.py

# 6. Verificar logs
tail -f logs/automation.log
```

### 2. Manutenção

```bash
# Backup do banco
cp database/leads.db backups/leads_$(date +%Y%m%d).db

# Rotação de logs
logrotate config/logrotate.conf

# Atualizar código
git pull origin main
pip install -r requirements.txt
```

## 📈 Melhorias Futuras

- [ ] Dashboard web para monitoramento
- [ ] Notificações via Slack/Telegram
- [ ] Integração com múltiplas fontes de dados
- [ ] API REST para consultas manuais
- [ ] Machine Learning para score de leads
- [ ] Integração com WhatsApp Business

## 🆘 Troubleshooting

### Problemas Comuns

1. **Cron job não executa:**
   ```bash
   # Verificar se o cron está rodando
   systemctl status cron
   
   # Verificar logs do sistema
   journalctl -u cron
   ```

2. **Erro de conexão com APIs:**
   ```bash
   # Testar conectividade
   curl -I https://api.cnpja.com.br
   
   # Verificar tokens/credenciais
   python -c "from src.utils.config import load_config; print(load_config())"
   ```

3. **Banco de dados corrompido:**
   ```bash
   # Verificar integridade
   sqlite3 database/leads.db "PRAGMA integrity_check;"
   
   # Restaurar backup
   cp backups/leads_latest.db database/leads.db
   ```

## 👥 Contribuindo

1. Fork do projeto
2. Criar branch da feature (`git checkout -b feature/nova-feature`)
3. Commit das mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abrir Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**🚀 Sistema desenvolvido para automatizar 100% da captação de leads contábeis com Python + Cron Jobs**