import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..models.company import Company
from ..utils.logger import setup_logger
from ..utils.validators import validate_cnpj, validate_email

logger = setup_logger()

class CNPJAService:
    """Serviço para integração com a API do CNPJá"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config['apis']['cnpja']
        self.base_url = self.config['base_url']
        self.token = self.config['token']
        self.timeout = self.config.get('timeout', 30)
        
        # Headers padrão
        self.headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ikasa-Leads-Automation/1.0'
        }
    
    async def get_companies_by_date(self, date: str) -> List[Company]:
        """Busca empresas criadas em uma data específica"""
        logger.info(f"Buscando empresas no CNPJá para data: {date}")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                # Endpoint para buscar empresas por data de abertura
                url = f"{self.base_url}/office"
                params = {
                    'founded.gte': date,
                    'address.state.in': 'MA',
                    'founded.lte': current_date,
                    'limit': 10
                }
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        companies = self._parse_companies(data.get('records', []))
                        logger.info(f"✅ {len(companies)} empresas encontradas no CNPJá")
                        return companies
                    
                    elif response.status == 401:
                        logger.error("❌ Token CNPJá inválido ou expirado")
                        raise Exception("Token CNPJá inválido")
                    
                    elif response.status == 429:
                        logger.warning("⚠️  Rate limit atingido, aguardando...")
                        await asyncio.sleep(60)  # Aguardar 1 minuto
                        return await self.get_companies_by_date(date)  # Retry
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro na API CNPJá: {response.status} - {error_text}")
                        raise Exception(f"Erro na API CNPJá: {response.status}")
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Erro de conexão com CNPJá: {e}")
            raise Exception(f"Erro de conexão: {e}")
        
        except Exception as e:
            logger.error(f"❌ Erro inesperado no CNPJá: {e}")
            raise
    
    def _parse_companies(self, companies_data: List[Dict]) -> List[Company]:
        """Converte dados da API em objetos Company"""
        companies = []
        
        for data in companies_data:
            try:
                # Validar CNPJ
                cnpj = data.get('taxId', '').strip()
                if not validate_cnpj(cnpj):
                    logger.warning(f"⚠️  CNPJ inválido ignorado: {cnpj}")
                    continue

                company_data = data.get('company', {})
                
                # Validar campos obrigatórios
                razao_social = company_data.get('name', '').strip()
                if not razao_social:
                    logger.warning(f"⚠️  Empresa sem razão social ignorada: {cnpj}")
                    continue
                
                # Converter data de abertura
                data_abertura_str = data.get('founded')
                try:
                    data_abertura = datetime.fromisoformat(data_abertura_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    logger.warning(f"⚠️  Data de abertura inválida para {cnpj}: {data_abertura_str}")
                    continue
                
                emails = data.get('emails', [])
                # Validar e limpar email
                email = emails[0].get('address', '').strip().lower() if emails else None
                if email and not validate_email(email):
                    logger.debug(f"E-mail inválido para {cnpj}: {email}")
                    email = None
                
                phones = data.get('phones', [])
                # Validar e limpar telefone
                phone = f"+55 {phones[0].get('area', '').strip()} {phones[0].get('number', '').strip()}" if phones else None

                address = data.get('address', {})
                main_activity = data.get('mainActivity', {})

                # Criar objeto Company
                company = Company(
                    cnpj=cnpj,
                    razao_social=razao_social,
                    nome_fantasia=data.get('nome_fantasia', '').strip() or None,
                    email=email,
                    telefone=phone,
                    endereco=self._format_address(address),
                    cidade=address.get('city', '').strip(),
                    estado=address.get('state', '').strip(),
                    cep=address.get('zip', '').strip() or None,
                    data_abertura=data_abertura,
                    atividade_principal=main_activity.get('text', '').strip() or None,
                    situacao=data.get('situacao', 'ATIVA').strip()
                )
                
                companies.append(company)
                logger.debug(f"✅ Empresa processada: {company.razao_social} ({company.cnpj})")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar empresa: {e}")
                continue
        
        return companies
    
    def _format_address(self, data: Dict) -> Optional[str]:
        """Formata endereço completo"""
        parts = []
        
        if data.get('street'):
            parts.append(data['street'].strip())
        
        if data.get('number'):
            parts.append(f"nº {data['number'].strip()}")
        
        if data.get('details'):
            parts.append(data['details'].strip())
        
        if data.get('district'):
            parts.append(data['district'].strip())
        
        return ', '.join(parts) if parts else None
    
    async def get_company_details(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes completos de uma empresa específica"""
        logger.debug(f"Buscando detalhes da empresa: {cnpj}")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.base_url}/empresas/{cnpj}"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"✅ Detalhes obtidos para: {cnpj}")
                        return data
                    
                    elif response.status == 404:
                        logger.warning(f"⚠️  Empresa não encontrada: {cnpj}")
                        return None
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro ao buscar detalhes: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar detalhes da empresa {cnpj}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Verifica se a API está funcionando"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"{self.base_url}/health"
                
                async with session.get(url, headers=self.headers) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.error(f"❌ Health check CNPJá falhou: {e}")
            return False