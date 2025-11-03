"""
Transaction log sistemi
Tüm işlemleri kaydeder ve rollback desteği sağlar
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class TransactionType(Enum):
    """Transaction tipleri"""
    INSTALL = "install"
    REMOVE = "remove"
    UPDATE = "update"
    UPGRADE = "upgrade"


class TransactionStatus(Enum):
    """Transaction durumları"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class Transaction:
    """Transaction sınıfı"""
    
    def __init__(self, transaction_type: TransactionType, packages: List[str]):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.type = transaction_type
        self.packages = packages
        self.status = TransactionStatus.PENDING
        self.timestamp = datetime.now().isoformat()
        self.actions = []
        self.error = None
    
    def add_action(self, action: str, details: Dict):
        """İşlem ekle"""
        self.actions.append({
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def set_status(self, status: TransactionStatus, error: Optional[str] = None):
        """Durumu güncelle"""
        self.status = status
        if error:
            self.error = error
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        return {
            'id': self.id,
            'type': self.type.value,
            'packages': self.packages,
            'status': self.status.value,
            'timestamp': self.timestamp,
            'actions': self.actions,
            'error': self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """Dict'ten oluştur"""
        trans = cls(
            TransactionType(data['type']),
            data['packages']
        )
        trans.id = data['id']
        trans.status = TransactionStatus(data['status'])
        trans.timestamp = data['timestamp']
        trans.actions = data.get('actions', [])
        trans.error = data.get('error')
        return trans


class TransactionLog:
    """Transaction log yöneticisi"""
    
    def __init__(self, log_dir: str = "/var/log/alp"):
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "transactions.log")
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Log dizinini oluştur"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
    
    def save_transaction(self, transaction: Transaction):
        """Transaction kaydet"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(transaction.to_dict()) + '\n')
    
    def load_transactions(self, limit: Optional[int] = None) -> List[Transaction]:
        """Transaction'ları yükle"""
        if not os.path.exists(self.log_file):
            return []
        
        transactions = []
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                
                if limit:
                    lines = lines[-limit:]
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        trans = Transaction.from_dict(data)
                        transactions.append(trans)
                    except json.JSONDecodeError as e:
                        print(f"Satır {line_num} parse hatası, atlanıyor: {e}")
                        continue
                    except Exception as e:
                        print(f"Satır {line_num} işleme hatası, atlanıyor: {e}")
                        continue
        except Exception as e:
            print(f"Transaction log dosyası okuma hatası: {e}")
        
        return transactions
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Belirli bir transaction getir"""
        transactions = self.load_transactions()
        
        for trans in transactions:
            if trans.id == transaction_id:
                return trans
        
        return None
    
    def get_last_transaction(self) -> Optional[Transaction]:
        """Son transaction'ı getir"""
        transactions = self.load_transactions(limit=1)
        
        if transactions:
            return transactions[0]
        
        return None
