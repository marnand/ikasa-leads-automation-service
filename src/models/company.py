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