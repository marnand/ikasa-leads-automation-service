import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from ..utils.config import get_database_path
from ..utils.logger import setup_logger

logger = setup_logger()

class DatabaseConnection:
    """Gerenciador de conexão com SQLite"""
    
    def __init__(self):
        self.db_path = get_database_path()
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Garante que o banco de dados e tabelas existam"""
        if not os.path.exists(self.db_path):
            logger.info(f"Criando banco de dados: {self.db_path}")
            self._create_tables()
        else:
            logger.debug(f"Banco de dados encontrado: {self.db_path}")
    
    def _create_tables(self):
        """Cria as tabelas necessárias"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de leads processados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cnpj TEXT UNIQUE NOT NULL,
                    razao_social TEXT NOT NULL,
                    nome_fantasia TEXT,
                    email TEXT,
                    telefone TEXT,
                    endereco TEXT,
                    cidade TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    cep TEXT,
                    data_abertura TEXT NOT NULL,
                    atividade_principal TEXT NOT NULL,
                    situacao TEXT NOT NULL,
                    crm_lead_id TEXT,
                    email_sent BOOLEAN DEFAULT FALSE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Tabela de logs de execução
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_date TEXT NOT NULL,
                    leads_found INTEGER DEFAULT 0,
                    leads_processed INTEGER DEFAULT 0,
                    leads_duplicated INTEGER DEFAULT 0,
                    leads_failed INTEGER DEFAULT 0,
                    execution_time_seconds REAL,
                    status TEXT DEFAULT 'running',
                    error_message TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_cnpj ON leads(cnpj)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_logs_date ON execution_logs(execution_date)")
            
            conn.commit()
            logger.info("Tabelas criadas com sucesso")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager para conexão com o banco"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Permite acesso por nome da coluna
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro na conexão com banco: {e}")
            raise
        finally:
            if conn:
                conn.close()