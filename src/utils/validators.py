import re
from typing import Optional

def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro
    
    Args:
        cnpj: CNPJ para validar
        
    Returns:
        True se válido, False caso contrário
    """
    # Remove formatação
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula primeiro dígito verificador
    sequence = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * sequence[i] for i in range(12))
    remainder = sum_digits % 11
    first_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cnpj[12]) != first_digit:
        return False
    
    # Calcula segundo dígito verificador
    sequence = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * sequence[i] for i in range(13))
    remainder = sum_digits % 11
    second_digit = 0 if remainder < 2 else 11 - remainder
    
    return int(cnpj[13]) == second_digit

def validate_email(email: Optional[str]) -> bool:
    """
    Valida formato de e-mail
    
    Args:
        email: E-mail para validar
        
    Returns:
        True se válido, False caso contrário
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_phone(phone: Optional[str]) -> Optional[str]:
    """
    Limpa e formata número de telefone
    
    Args:
        phone: Telefone para limpar
        
    Returns:
        Telefone limpo ou None
    """
    if not phone:
        return None
    
    # Remove tudo que não é dígito
    clean = ''.join(filter(str.isdigit, phone))
    
    # Verifica se tem tamanho válido (10 ou 11 dígitos)
    if len(clean) not in [10, 11]:
        return None
    
    return clean

def clean_cep(cep: Optional[str]) -> Optional[str]:
    """Limpa e formata CEP"""
    if not cep:
        return None
    
    # Remove tudo que não é dígito
    digits = ''.join(filter(str.isdigit, cep))
    
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    
    return cep