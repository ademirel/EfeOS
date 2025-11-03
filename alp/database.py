"""
SQLite database management
Tracks installed packages and their status
"""

import sqlite3
import json
from typing import List, Optional, Dict
from datetime import datetime


class PackageDatabase:
    """Package database class"""
    
    def __init__(self, db_path: str = "/var/lib/alp/packages.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_database()
    
    def _ensure_db_dir(self):
        """Create database directory"""
        import os
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _init_database(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                version TEXT NOT NULL,
                description TEXT,
                architecture TEXT,
                maintainer TEXT,
                homepage TEXT,
                license TEXT,
                size INTEGER,
                checksum TEXT,
                install_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'installed'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id INTEGER,
                dependency_name TEXT,
                dependency_version TEXT,
                FOREIGN KEY (package_id) REFERENCES packages(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id INTEGER,
                file_path TEXT,
                FOREIGN KEY (package_id) REFERENCES packages(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                url TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                priority INTEGER DEFAULT 100
            )
        """)
        
        self.conn.commit()
    
    def add_package(self, metadata: Dict) -> int:
        """Add new package or update existing"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM packages WHERE name = ?", (metadata['name'],))
        existing = cursor.fetchone()
        
        if existing:
            package_id = existing[0]
            cursor.execute("DELETE FROM dependencies WHERE package_id = ?", (package_id,))
            cursor.execute("DELETE FROM files WHERE package_id = ?", (package_id,))
            
            cursor.execute("""
                UPDATE packages 
                SET version=?, description=?, architecture=?, 
                    maintainer=?, homepage=?, license=?, size=?, checksum=?,
                    install_date=CURRENT_TIMESTAMP
                WHERE id=?
            """, (
                metadata['version'],
                metadata.get('description', ''),
                metadata.get('architecture', 'x86_64'),
                metadata.get('maintainer', ''),
                metadata.get('homepage', ''),
                metadata.get('license', ''),
                metadata.get('size', 0),
                metadata.get('checksum', ''),
                package_id
            ))
        else:
            cursor.execute("""
                INSERT INTO packages (name, version, description, architecture, 
                                    maintainer, homepage, license, size, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata['name'],
                metadata['version'],
                metadata.get('description', ''),
                metadata.get('architecture', 'x86_64'),
                metadata.get('maintainer', ''),
                metadata.get('homepage', ''),
                metadata.get('license', ''),
                metadata.get('size', 0),
                metadata.get('checksum', '')
            ))
            
            package_id = cursor.lastrowid
            if package_id is None:
                raise ValueError("Package could not be added")
        
        for dep in metadata.get('dependencies', []):
            dep_parts = dep.split('>=') if '>=' in dep else [dep, '']
            cursor.execute("""
                INSERT INTO dependencies (package_id, dependency_name, dependency_version)
                VALUES (?, ?, ?)
            """, (package_id, dep_parts[0].strip(), dep_parts[1].strip() if len(dep_parts) > 1 else ''))
        
        for file_path in metadata.get('files', []):
            cursor.execute("""
                INSERT INTO files (package_id, file_path)
                VALUES (?, ?)
            """, (package_id, file_path))
        
        self.conn.commit()
        return package_id
    
    def remove_package(self, package_name: str) -> bool:
        """Remove package"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM packages WHERE name = ?", (package_name,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        package_id = row[0]
        
        cursor.execute("DELETE FROM dependencies WHERE package_id = ?", (package_id,))
        cursor.execute("DELETE FROM files WHERE package_id = ?", (package_id,))
        cursor.execute("DELETE FROM packages WHERE id = ?", (package_id,))
        
        self.conn.commit()
        return True
    
    def get_package(self, package_name: str) -> Optional[Dict]:
        """Get package information (with all metadata)"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT * FROM packages WHERE name = ?", (package_name,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        package_data = dict(row)
        
        cursor.execute("""
            SELECT dependency_name, dependency_version 
            FROM dependencies WHERE package_id = ?
        """, (package_data['id'],))
        
        dependencies = []
        for dep_row in cursor.fetchall():
            dep_str = dep_row[0]
            if dep_row[1]:
                dep_str += f">={dep_row[1]}"
            dependencies.append(dep_str)
        
        package_data['dependencies'] = dependencies
        
        cursor.execute("""
            SELECT file_path FROM files WHERE package_id = ?
        """, (package_data['id'],))
        
        files = []
        for file_row in cursor.fetchall():
            files.append(file_row[0])
        
        package_data['files'] = files
        
        package_data.setdefault('conflicts', [])
        package_data.setdefault('provides', [])
        
        return package_data
    
    def list_packages(self) -> List[Dict]:
        """List all packages"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, version, description, size FROM packages ORDER BY name")
        
        packages = []
        for row in cursor.fetchall():
            packages.append(dict(row))
        
        return packages
    
    def is_installed(self, package_name: str) -> bool:
        """Is package installed?"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM packages WHERE name = ?", (package_name,))
        count = cursor.fetchone()[0]
        return count > 0
    
    def add_repository(self, name: str, url: str, priority: int = 100) -> None:
        """Add repository"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO repositories (name, url, priority)
            VALUES (?, ?, ?)
        """, (name, url, priority))
        self.conn.commit()
    
    def list_repositories(self) -> List[Dict]:
        """Get repository list"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM repositories WHERE enabled = 1 ORDER BY priority DESC")
        
        repos = []
        for row in cursor.fetchall():
            repos.append(dict(row))
        
        return repos
    
    def close(self):
        """Close database connection"""
        self.conn.close()
