from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .company import Company

@dataclass
class Lead:
    """Modelo para dados do lead processado"""
    id: Optional[int]
    company: Company
    crm_lead_id: Optional[str]
    email_sent: bool
    created_at: datetime
    updated_at: Optional[datetime]
    status: str  # 'processed', 'failed', 'duplicate'
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'company': self.company.to_dict(),
            'crm_lead_id': self.crm_lead_id,
            'email_sent': self.email_sent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status
        }