"""
Paket format ve işleme modülü
.alp format: YAML metadata + tar.gz arşiv
"""

import os
import yaml
import tarfile
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class PackageMetadata:
    """Paket metadata yapısı"""
    name: str
    version: str
    description: str
    architecture: str
    dependencies: List[str]
    conflicts: List[str]
    provides: List[str]
    maintainer: str
    homepage: str
    license: str
    size: int
    checksum: str
    files: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PackageMetadata':
        return cls(**data)


class Package:
    """Paket sınıfı - .alp dosya formatı"""
    
    def __init__(self, metadata: PackageMetadata, package_path: Optional[str] = None):
        self.metadata = metadata
        self.package_path = package_path
    
    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """Dosya SHA256 checksum hesapla"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_checksum(self) -> bool:
        """Paket checksum doğrula"""
        if not self.package_path or not os.path.exists(self.package_path):
            return False
        
        calculated = self.calculate_checksum(self.package_path)
        return calculated == self.metadata.checksum
    
    @classmethod
    def create_package(cls, name: str, version: str, source_dir: str, 
                       output_path: str, metadata_dict: Dict) -> 'Package':
        """Yeni paket oluştur"""
        
        tar_path = f"{output_path}.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(source_dir, arcname=name)
        
        file_list = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)
                file_list.append(rel_path)
        
        checksum = cls.calculate_checksum(tar_path)
        size = os.path.getsize(tar_path)
        
        metadata_dict.update({
            'name': name,
            'version': version,
            'checksum': checksum,
            'size': size,
            'files': file_list
        })
        
        metadata = PackageMetadata.from_dict(metadata_dict)
        
        metadata_path = f"{output_path}.yaml"
        with open(metadata_path, 'w') as f:
            yaml.dump(metadata.to_dict(), f, default_flow_style=False)
        
        final_package_path = f"{output_path}.alp"
        with tarfile.open(final_package_path, "w:gz") as pkg:
            pkg.add(metadata_path, arcname="metadata.yaml")
            pkg.add(tar_path, arcname="data.tar.gz")
        
        os.remove(metadata_path)
        os.remove(tar_path)
        
        return cls(metadata, final_package_path)
    
    @classmethod
    def load_package(cls, package_path: str) -> 'Package':
        """Mevcut paketi yükle"""
        with tarfile.open(package_path, "r:gz") as pkg:
            metadata_file = pkg.extractfile("metadata.yaml")
            if metadata_file is None:
                raise ValueError("metadata.yaml bulunamadı")
            metadata_dict = yaml.safe_load(metadata_file)
            metadata = PackageMetadata.from_dict(metadata_dict)
        
        return cls(metadata, package_path)
    
    def extract_data(self, dest_dir: str) -> None:
        """Paket içeriğini çıkart"""
        with tarfile.open(self.package_path, "r:gz") as pkg:
            data_tar = pkg.extractfile("data.tar.gz")
            with tarfile.open(fileobj=data_tar, mode="r:gz") as data:
                data.extractall(dest_dir)
    
    def __repr__(self) -> str:
        return f"Package({self.metadata.name}-{self.metadata.version})"
