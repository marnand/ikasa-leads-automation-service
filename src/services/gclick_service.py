import aiohttp
import asyncio
from typing import Dict, Any, Optional
from ..models.company import Company
from ..utils.logger import setup_logger

logger = setup_logger()

class GClickService:
    """Serviço para integração com a API do G-Click"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config['apis']['gclick']
        self.base_url = self.config['base_url']
        self.token = self.config['token']
        self.timeout = self.config.get('timeout', 30)
        
        # Headers padrão
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Ikasa-Leads-Automation/1.0'
        }
    
    async def send_email(self, company: Company) -> bool:
        """Envia e-mail de contato para a empresa"""
        if not company.email:
            logger.warning(f"⚠️  Empresa sem e-mail: {company.razao_social}")
            return False
        
        logger.info(f"Enviando e-mail para: {company.email}")
        
        try:
            # Preparar dados do e-mail
            email_data = self._prepare_email_data(company)
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.base_url}/emails/send"
                
                async with session.post(url, headers=self.headers, json=email_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        message_id = data.get('message_id')
                        logger.info(f"✅ E-mail enviado: {message_id}")
                        return True
                    
                    elif response.status == 400:
                        error_data = await response.json()
                        logger.error(f"❌ Dados inválidos para e-mail: {error_data}")
                        return False
                    
                    elif response.status == 401:
                        logger.error("❌ Token G-Click inválido")
                        raise Exception("Token G-Click inválido")
                    
                    elif response.status == 429:
                        logger.warning("⚠️  Rate limit G-Click atingido, aguardando...")
                        await asyncio.sleep(60)
                        return await self.send_email(company)  # Retry
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro na API G-Click: {response.status} - {error_text}")
                        return False
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Erro de conexão com G-Click: {e}")
            return False
        
        except Exception as e:
            logger.error(f"❌ Erro inesperado no G-Click: {e}")
            return False
    
    def _prepare_email_data(self, company: Company) -> Dict[str, Any]:
        """Prepara dados do e-mail"""
        # Template personalizado baseado nos dados da empresa
        subject = f"Oportunidade de Parceria - {company.razao_social}"
        
        # Corpo do e-mail personalizado
        body = self._generate_email_body(company)
        
        return {
            'to': [
                {
                    'email': company.email,
                    'name': company.nome_fantasia or company.razao_social
                }
            ],
            'subject': subject,
            'html_content': body,
            'sender': {
                'email': 'contato@ikasa.com.br',
                'name': 'Ikasa Contabilidade'
            },
            'template_id': 'lead_contabil_template',  # Template pré-configurado
            'tags': ['automacao', 'lead', 'contabil'],
            'tracking': {
                'opens': True,
                'clicks': True,
                'unsubscribe': True
            },
            'custom_data': {
                'cnpj': company.cnpj,
                'fonte': 'cnpja_automation',
                'data_captacao': company.data_abertura.strftime('%Y-%m-%d')
            }
        }
    
    def _generate_email_body(self, company: Company) -> str:
        """Gera corpo do e-mail personalizado"""
        nome_empresa = company.nome_fantasia or company.razao_social
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Ikasa Contabilidade</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="https://ikasa.com.br/logo.png" alt="Ikasa" style="max-width: 200px;">
                </div>
                
                <h2 style="color: #2c5aa0;">Parabéns pela abertura da {nome_empresa}!</h2>
                
                <p>Olá,</p>
                
                <p>Soubemos que a <strong>{nome_empresa}</strong> foi recentemente constituída e gostaríamos de parabenizá-los por este importante passo!</p>
                
                <p>A <strong>Ikasa Contabilidade</strong> é especializada em atender empresas em início de atividade, oferecendo:</p>
                
                <ul>
                    <li>✅ Contabilidade completa e personalizada</li>
                    <li>✅ Assessoria fiscal e tributária</li>
                    <li>✅ Folha de pagamento e eSocial</li>
                    <li>✅ Consultoria empresarial</li>
                    <li>✅ Suporte completo para MEI, ME e EPP</li>
                </ul>
                
                <p><strong>Oferta especial para empresas novas:</strong></p>
                <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #2c5aa0; margin: 20px 0;">
                    <p style="margin: 0;"><strong>🎯 Primeira consulta GRATUITA</strong></p>
                    <p style="margin: 5px 0 0 0;">Análise completa da sua situação fiscal e tributária</p>
                </div>
                
                <p>Nossos especialistas estão prontos para ajudar sua empresa a crescer com segurança e conformidade fiscal.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://ikasa.com.br/contato" 
                       style="background-color: #2c5aa0; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Agendar Consulta Gratuita
                    </a>
                </div>
                
                <p>Ou entre em contato conosco:</p>
                <ul>
                    <li>📞 Telefone: (11) 3000-0000</li>
                    <li>📧 E-mail: contato@ikasa.com.br</li>
                    <li>🌐 Site: www.ikasa.com.br</li>
                </ul>
                
                <p>Estamos ansiosos para fazer parte do sucesso da {nome_empresa}!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe Ikasa Contabilidade</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                
                <div style="font-size: 12px; color: #666; text-align: center;">
                    <p>Este e-mail foi enviado para {company.email}</p>
                    <p>Se não deseja mais receber nossos e-mails, <a href="{{unsubscribe_url}}">clique aqui</a></p>
                    <p>Ikasa Contabilidade - CNPJ: 00.000.000/0001-00</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def get_email_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Verifica status de um e-mail enviado"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.base_url}/emails/{message_id}/status"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status do e-mail {message_id}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Verifica se a API está funcionando"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"{self.base_url}/health"
                
                async with session.get(url, headers=self.headers) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.error(f"❌ Health check G-Click falhou: {e}")
            return False