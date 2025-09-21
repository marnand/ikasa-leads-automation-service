"""
Serviços de integração com APIs externas
"""

from .cnpja_service import CNPJAService
from .crm_service import CRMService
from .gclick_service import GClickService

__all__ = ['CNPJAService', 'CRMService', 'GClickService']