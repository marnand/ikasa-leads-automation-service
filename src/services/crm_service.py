import aiohttp
import asyncio
from typing import Dict, Any, Optional
from ..models.company import Company
from ..utils.logger import setup_logger

logger = setup_logger()

class CRMService:
    """Serviço para integração com a API do 4C CRM"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config['apis']['crm_4c']
        self.base_url = self.config['base_url']
        self.api_key = self.config['api_key']
        self.timeout = self.config.get('timeout', 30)
        
        # Headers padrão
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ikasa-Leads-Automation/1.0'
        }
    
    async def create_lead(self, company: Company) -> Optional[str]:
        """Cria um lead no CRM"""
        logger.info(f"Criando lead no CRM: {company.razao_social}")
        
        try:
            # Preparar dados do lead
            lead_data = self._prepare_lead_data(company)
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.base_url}/leads"
                
                async with session.post(url, headers=self.headers, json=lead_data) as response:
                    if response.status == 201:
                        data = await response.json()
                        lead_id = data.get('id') or data.get('lead_id')
                        logger.info(f"✅ Lead criado no CRM: {lead_id}")
                        return str(lead_id)
                    
                    elif response.status == 409:
                        # Lead já existe
                        logger.warning(f"⚠️  Lead já existe no CRM: {company.cnpj}")
                        data = await response.json()
                        existing_id = data.get('existing_id')
                        return str(existing_id) if existing_id else None
                    
                    elif response.status == 401:
                        logger.error("❌ API Key do CRM inválida")
                        raise Exception("API Key do CRM inválida")
                    
                    elif response.status == 429:
                        logger.warning("⚠️  Rate limit CRM atingido, aguardando...")
                        await asyncio.sleep(30)
                        return await self.create_lead(company)  # Retry
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro na API CRM: {response.status} - {error_text}")
                        raise Exception(f"Erro na API CRM: {response.status}")
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Erro de conexão com CRM: {e}")
            raise Exception(f"Erro de conexão CRM: {e}")
        
        except Exception as e:
            logger.error(f"❌ Erro inesperado no CRM: {e}")
            raise
    
    def _prepare_lead_data(self, company: Company) -> Dict[str, Any]:
        """Prepara dados da empresa para o formato do CRM"""
        return {
            'source': 'CNPJá Automation',
            'status': 'new',
            'priority': 'medium',
            'company': {
                'cnpj': company.formatted_cnpj,
                'name': company.razao_social,
                'trade_name': company.nome_fantasia,
                'email': company.email,
                'phone': company.telefone,
                'address': company.endereco,
                'city': company.cidade,
                'state': company.estado,
                'zip_code': company.cep,
                'opening_date': company.data_abertura.isoformat(),
                'main_activity': company.atividade_principal,
                'status': company.situacao
            },
            'tags': ['automacao', 'cnpja', 'empresa-nova'],
            'custom_fields': {
                'data_captacao': company.data_abertura.strftime('%Y-%m-%d'),
                'fonte_captacao': 'CNPJá API',
                'segmento': 'Contábil'
            }
        }
    
    async def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza um lead existente"""
        logger.info(f"Atualizando lead no CRM: {lead_id}")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.base_url}/leads/{lead_id}"
                
                async with session.put(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        logger.info(f"✅ Lead atualizado no CRM: {lead_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro ao atualizar lead: {response.status} - {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar lead {lead_id}: {e}")
            return False
    
    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca um lead específico"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.base_url}/leads/{lead_id}"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar lead {lead_id}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Verifica se a API está funcionando"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"{self.base_url}/health"
                
                async with session.get(url, headers=self.headers) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.error(f"❌ Health check CRM falhou: {e}")
            return False