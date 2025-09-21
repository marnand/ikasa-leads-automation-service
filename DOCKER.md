# 🐳 Docker Setup - Ikasa Leads Automation

Este documento explica como executar o projeto usando Docker.

## 📋 Pré-requisitos

- Docker
- Docker Compose

## 🚀 Execução Rápida

### Desenvolvimento
```bash
# Construir e executar (logs visíveis)
docker-compose up --build

# Ou usar o script helper
chmod +x scripts/docker-dev.sh
./scripts/docker-dev.sh
```

### Produção
```bash
# Executar em background
docker-compose -f docker-compose.prod.yml up -d

# Verificar status
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📁 Estrutura de Volumes

O container monta os seguintes volumes:

- `./database` → `/app/database` - Banco de dados SQLite
- `./logs` → `/app/logs` - Arquivos de log
- `./config` → `/app/config` - Configurações

## ⚙️ Configuração

1. **Edite o arquivo de configuração:**
   ```bash
   nano config/settings.yaml
   ```

2. **Configure suas APIs:**
   - Token CNPJA
   - API Key CRM 4C
   - Token GClick

## 🕐 Execução Agendada

### Opção 1: Ofelia (Recomendado para produção)
O `docker-compose.prod.yml` inclui o Ofelia para execução automática às 8h.

### Opção 2: Cron do host
```bash
# Adicionar ao crontab do host
0 8 * * * cd /caminho/para/projeto && docker-compose run --rm ikasa-leads-automation
```

## 🔧 Comandos Úteis

```bash
# Construir imagem
docker-compose build

# Executar uma vez
docker-compose run --rm ikasa-leads-automation

# Ver logs em tempo real
docker-compose logs -f ikasa-leads-automation

# Parar containers
docker-compose down

# Limpar volumes (CUIDADO: apaga dados)
docker-compose down -v

# Entrar no container
docker-compose exec ikasa-leads-automation bash
```

## 🐛 Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker-compose logs ikasa-leads-automation

# Verificar configuração
docker-compose config
```

### Problemas de permissão
```bash
# Ajustar permissões dos diretórios
sudo chown -R $USER:$USER database/ logs/
```

### Limpar cache Docker
```bash
# Remover imagens não utilizadas
docker system prune -a
```

## 📊 Monitoramento

### Ver recursos utilizados
```bash
docker stats ikasa-leads-automation
```

### Health check
```bash
docker-compose ps
# Status deve mostrar "healthy"
```