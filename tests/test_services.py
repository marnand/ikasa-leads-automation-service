import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from src.services.cnpja_service import CNPJAService
from src.services.crm_service import CRMService
from src.services.gclick_service import GClickService
from src.models.company import Company

@pytest.fixture
def sample_config():
    return {
        'apis': {
            'cnpja': {
                'base_url': 'https://api.cnpja.test.com',
                'token': 'test_token',
                'timeout': 30
            },
            'crm_4c': {
                'base_url': 'https://api.4c.test.com',
                'api_key': 'test_api_key',
                'timeout': 30
            },
            'gclick': {
                'base_url': 'https://api.gclick.test.com',
                'token': 'test_token',
                'timeout': 30
            }
        }
    }

@pytest.fixture
def sample_company():
    return Company(
        cnpj='12345678000195',
        razao_social='Empresa Teste LTDA',
        nome_fantasia='Empresa Teste',
        email='contato@empresateste.com.br',
        telefone='(11) 99999-9999',
        endereco='Rua Teste, 123',
        cidade='São Paulo',
        estado='SP',
        cep='01234-567',
        data_abertura=datetime(2024, 1, 15),
        atividade_principal='Atividade de teste',
        situacao='ATIVA'
    )

class TestCNPJAService:
    
    @pytest.mark.asyncio
    async def test_get_companies_by_date(self, sample_config):
        """Testa a busca de empresas por data"""
        cnpja = CNPJAService(sample_config)
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'data': [sample_company.to_dict()]
        }
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            companies = await cnpja.get_companies_by_date('2024-01-15')
            assert len(companies) == 1
            assert companies[0].cnpj == sample_company.cnpj