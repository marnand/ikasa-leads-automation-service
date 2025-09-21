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