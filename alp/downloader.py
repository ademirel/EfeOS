"""
Paket indirme ve doğrulama modülü
"""

import os
import requests
import hashlib
from typing import Optional, Callable


class Downloader:
    """Paket indirici"""
    
    def __init__(self, cache_dir: str = "/var/cache/alp"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Cache dizinini oluştur"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def download(self, url: str, destination: str, 
                 progress_callback: Optional[Callable] = None) -> bool:
        """Dosya indir"""
        try:
            if url.startswith('file://'):
                import shutil
                source_path = url.replace('file://', '')
                
                abs_source = os.path.abspath(source_path)
                if not os.path.exists(abs_source):
                    raise FileNotFoundError(f"Kaynak dosya bulunamadı: {abs_source}")
                
                if not abs_source.endswith('.alp'):
                    raise ValueError("Sadece .alp dosyaları indirilebilir")
                
                shutil.copy2(abs_source, destination)
                
                if progress_callback:
                    file_size = os.path.getsize(destination)
                    progress_callback(100, file_size, file_size)
                
                return True
            else:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                progress_callback(progress, downloaded, total_size)
                
                return True
        
        except Exception as e:
            print(f"İndirme hatası: {e}")
            return False
    
    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Checksum doğrula"""
        if not os.path.exists(file_path):
            return False
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        calculated = sha256_hash.hexdigest()
        return calculated == expected_checksum
    
    def get_cached_package(self, package_name: str, version: str) -> Optional[str]:
        """Cache'deki paketi getir"""
        cached_path = os.path.join(self.cache_dir, f"{package_name}-{version}.alp")
        
        if os.path.exists(cached_path):
            return cached_path
        
        return None
    
    def clean_cache(self) -> int:
        """Cache temizle"""
        count = 0
        
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        count += 1
                except Exception as e:
                    print(f"Silme hatası {filename}: {e}")
        
        return count
