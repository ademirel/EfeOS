"""
Repository yönetimi ve paket indeksi
"""

import os
import json
import requests
from typing import List, Dict, Optional


class Repository:
    """Repository sınıfı"""
    
    def __init__(self, database, cache_dir: str = "/var/cache/lpm/repos"):
        self.database = database
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        self._index_cache = {}
    
    def _ensure_cache_dir(self):
        """Cache dizinini oluştur"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def update_index(self, repo_url: str) -> bool:
        """Repository indeksini güncelle"""
        try:
            index_url = f"{repo_url}/index.json"
            
            if repo_url.startswith('file://'):
                file_path = repo_url.replace('file://', '') + '/index.json'
                with open(file_path, 'r') as f:
                    index_data = json.load(f)
            else:
                response = requests.get(index_url, timeout=30)
                response.raise_for_status()
                index_data = response.json()
            
            repo_name = index_data.get('name', 'unknown')
            cache_file = os.path.join(self.cache_dir, f"{repo_name}.json")
            
            with open(cache_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            self._index_cache[repo_name] = index_data
            
            return True
        
        except Exception as e:
            print(f"İndeks güncelleme hatası: {e}")
            return False
    
    def update_all_indexes(self) -> Dict[str, bool]:
        """Tüm repository indekslerini güncelle"""
        repos = self.database.list_repositories()
        results = {}
        
        for repo in repos:
            success = self.update_index(repo['url'])
            results[repo['name']] = success
        
        return results
    
    def search_package(self, query: str) -> List[Dict]:
        """Paket ara"""
        results = []
        repos = self.database.list_repositories()
        
        for repo in repos:
            index = self._load_index(repo['name'])
            
            if not index:
                continue
            
            packages = index.get('packages', [])
            
            for pkg in packages:
                if query.lower() in pkg.get('name', '').lower() or \
                   query.lower() in pkg.get('description', '').lower():
                    pkg['repository'] = repo['name']
                    results.append(pkg)
        
        return results
    
    def get_package_metadata(self, package_name: str) -> Optional[Dict]:
        """Paket metadata getir"""
        repos = self.database.list_repositories()
        
        for repo in repos:
            index = self._load_index(repo['name'])
            
            if not index:
                continue
            
            packages = index.get('packages', [])
            
            for pkg in packages:
                if pkg.get('name') == package_name:
                    pkg['repository'] = repo['name']
                    pkg['repository_url'] = repo['url']
                    return pkg
        
        return None
    
    def get_package_url(self, package_name: str, version: str) -> Optional[str]:
        """Paket indirme URL'ini getir"""
        metadata = self.get_package_metadata(package_name)
        
        if not metadata:
            return None
        
        repo_url = metadata.get('repository_url')
        
        if not repo_url:
            return None
        
        return f"{repo_url}/packages/{package_name}-{version}.lpkg"
    
    def _load_index(self, repo_name: str) -> Optional[Dict]:
        """Repository indeksini yükle"""
        if repo_name in self._index_cache:
            return self._index_cache[repo_name]
        
        cache_file = os.path.join(self.cache_dir, f"{repo_name}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                index_data = json.load(f)
                self._index_cache[repo_name] = index_data
                return index_data
        except Exception as e:
            print(f"İndeks yükleme hatası: {e}")
            return None
    
    def list_available_packages(self) -> List[Dict]:
        """Tüm mevcut paketleri listele"""
        all_packages = []
        repos = self.database.list_repositories()
        
        for repo in repos:
            index = self._load_index(repo['name'])
            
            if not index:
                continue
            
            packages = index.get('packages', [])
            
            for pkg in packages:
                pkg['repository'] = repo['name']
                all_packages.append(pkg)
        
        return all_packages
