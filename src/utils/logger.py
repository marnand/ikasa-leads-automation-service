import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .config import load_config

def setup_logger(name: str = "leads_automation") -> logging.Logger:
    """
    Configura e retorna o logger do sistema
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    config = load_config()
    log_config = config['logging']
    
    # Criar diretório de logs se não existir
    log_file = log_config['file']
    if not os.path.isabs(log_file):
        project_root = Path(__file__).parent.parent.parent
        log_file = project_root / log_file
    
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_config['level']))
    
    # Remover handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=log_config.get('max_bytes', 10485760),  # 10MB
        backupCount=log_config.get('backup_count', 5),
        encoding='utf-8'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger