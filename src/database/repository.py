from datetime import datetime
from typing import List, Optional, Dict, Any
from ..models.company import Company
from ..models.lead import Lead
from .connection import DatabaseConnection
from ..utils.logger import setup_logger

logger = setup_logger()

class LeadRepository:
    """Repository para operações com leads no banco de dados"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db = DatabaseConnection()
    
    def lead_exists(self, cnpj: str) -> bool:
        """Verifica se um lead já existe no banco"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM leads WHERE cnpj = ?", (cnpj,))
            return cursor.fetchone() is not None
    
    def save_lead(self, company: Company, crm_lead_id: Optional[str] = None, email_sent: bool = False) -> int:
        """Salva um lead no banco de dados"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO leads (
                    cnpj, razao_social, nome_fantasia, email, telefone,
                    endereco, cidade, estado, cep, data_abertura,
                    atividade_principal, situacao, crm_lead_id,
                    email_sent, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company.cnpj,
                company.razao_social,
                company.nome_fantasia,
                company.email,
                company.telefone,
                company.endereco,
                company.cidade,
                company.estado,
                company.cep,
                company.data_abertura.isoformat(),
                company.atividade_principal,
                company.situacao,
                crm_lead_id,
                email_sent,
                now,
                'processed' if crm_lead_id else 'pending'
            ))
            
            lead_id = cursor.lastrowid
            conn.commit()
            
            logger.debug(f"Lead salvo no banco: ID {lead_id}, CNPJ {company.cnpj}")
            return lead_id
    
    def update_lead_status(self, cnpj: str, status: str, crm_lead_id: Optional[str] = None, email_sent: Optional[bool] = None):
        """Atualiza status de um lead"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Construir query dinamicamente
            updates = ["status = ?", "updated_at = ?"]
            params = [status, now]
            
            if crm_lead_id is not None:
                updates.append("crm_lead_id = ?")
                params.append(crm_lead_id)
            
            if email_sent is not None:
                updates.append("email_sent = ?")
                params.append(email_sent)
            
            params.append(cnpj)
            
            query = f"UPDATE leads SET {', '.join(updates)} WHERE cnpj = ?"
            cursor.execute(query, params)
            conn.commit()
            
            logger.debug(f"Lead atualizado: CNPJ {cnpj}, Status {status}")
    
    def get_leads_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Busca leads por data de criação"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM leads 
                WHERE DATE(created_at) = DATE(?)
                ORDER BY created_at DESC
            """, (date,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_lead_by_cnpj(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """Busca lead por CNPJ"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE cnpj = ?", (cnpj,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Retorna estatísticas dos últimos N dias"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de leads
            cursor.execute("""
                SELECT COUNT(*) as total_leads,
                       SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) as processed,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                       SUM(CASE WHEN email_sent = 1 THEN 1 ELSE 0 END) as emails_sent
                FROM leads 
                WHERE created_at >= datetime('now', '-{} days')
            """.format(days))
            
            stats = dict(cursor.fetchone())
            
            # Leads por dia
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM leads 
                WHERE created_at >= datetime('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """.format(days))
            
            stats['daily_counts'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
    
    def log_execution(self, execution_date: str, leads_found: int = 0, leads_processed: int = 0, 
                     leads_duplicated: int = 0, leads_failed: int = 0, 
                     execution_time: float = 0, status: str = 'completed', 
                     error_message: Optional[str] = None) -> int:
        """Registra log de execução"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO execution_logs (
                    execution_date, leads_found, leads_processed,
                    leads_duplicated, leads_failed, execution_time_seconds,
                    status, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_date, leads_found, leads_processed,
                leads_duplicated, leads_failed, execution_time,
                status, error_message, now
            ))
            
            log_id = cursor.lastrowid
            conn.commit()
            
            logger.debug(f"Log de execução salvo: ID {log_id}")
            return log_id