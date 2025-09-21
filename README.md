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

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.
