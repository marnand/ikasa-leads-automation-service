import yaml
import os
from pathlib import Path
from typing import Dict, Any
import re

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Carrega configurações do arquivo YAML
    
    Args:
        config_path: Caminho para o arquivo de configuração
        
    Returns:
        Dict com as configurações
    """
    if config_path is None:
        # Buscar arquivo de configuração na raiz do projeto
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "settings.yaml"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Substituir variáveis de ambiente no formato ${VAR_NAME}
        content = replace_env_vars(content)
        config = yaml.safe_load(content)
    
    # Validar configurações obrigatórias
    required_sections = ['apis', 'database', 'logging']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Seção obrigatória '{section}' não encontrada no arquivo de configuração")
    
    return config

def replace_env_vars(content: str) -> str:
    """Substitui variáveis de ambiente no formato ${VAR_NAME} pelos seus valores"""
    def replace_var(match):
        var_name = match.group(1)
        # Primeiro tenta obter da variável de ambiente
        value = os.getenv(var_name)
        if value is not None:
            return value
        # Se não encontrou, mantém o valor original
        return match.group(0)
    
    # Pattern para encontrar ${VAR_NAME}
    pattern = r'\$\{([^}]+)\}'
    return re.sub(pattern, replace_var, content)

def get_database_path() -> str:
    """Retorna o caminho completo para o banco de dados"""
    config = load_config()
    db_path = config['database']['path']
    
    # Se for caminho relativo, tornar absoluto baseado na raiz do projeto
    if not os.path.isabs(db_path):
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / db_path
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    return str(db_path)