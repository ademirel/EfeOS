#!/usr/bin/env python3
"""
Demo paket oluşturma scripti
LPM formatında örnek paketler oluşturur
"""

import os
import sys
from lpm.package import Package, PackageMetadata

def create_hello_world_package():
    """Hello World paketi oluştur"""
    
    os.makedirs("demo_packages/hello-world/usr/bin", exist_ok=True)
    
    with open("demo_packages/hello-world/usr/bin/hello", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("echo 'Hello, World from LPM!'\n")
    
    os.chmod("demo_packages/hello-world/usr/bin/hello", 0o755)
    
    metadata = {
        'description': 'Basit Hello World uygulaması',
        'architecture': 'x86_64',
        'dependencies': [],
        'conflicts': [],
        'provides': ['hello'],
        'maintainer': 'demo@lpm.local',
        'homepage': 'https://example.com/hello-world',
        'license': 'MIT'
    }
    
    pkg = Package.create_package(
        name='hello-world',
        version='1.0.0',
        source_dir='demo_packages/hello-world',
        output_path='demo_repo/packages/hello-world-1.0.0',
        metadata_dict=metadata
    )
    
    print(f"✅ {pkg} oluşturuldu")
    print(f"   Checksum: {pkg.metadata.checksum}")
    print(f"   Boyut: {pkg.metadata.size} bytes")

def create_example_lib_package():
    """Example Library paketi oluştur"""
    
    os.makedirs("demo_packages/example-lib/usr/lib", exist_ok=True)
    
    with open("demo_packages/example-lib/usr/lib/libexample.so", "w") as f:
        f.write("// Örnek kütüphane binary dosyası\n")
        f.write("void example_function() { return; }\n")
    
    metadata = {
        'description': 'Örnek kütüphane paketi',
        'architecture': 'x86_64',
        'dependencies': [],
        'conflicts': [],
        'provides': ['libexample'],
        'maintainer': 'demo@lpm.local',
        'homepage': 'https://example.com/example-lib',
        'license': 'GPL-3.0'
    }
    
    pkg = Package.create_package(
        name='example-lib',
        version='2.1.0',
        source_dir='demo_packages/example-lib',
        output_path='demo_repo/packages/example-lib-2.1.0',
        metadata_dict=metadata
    )
    
    print(f"✅ {pkg} oluşturuldu")
    print(f"   Checksum: {pkg.metadata.checksum}")
    print(f"   Boyut: {pkg.metadata.size} bytes")

if __name__ == '__main__':
    print("📦 Demo paketleri oluşturuluyor...\n")
    
    try:
        create_hello_world_package()
        print()
        create_example_lib_package()
        print("\n✅ Tüm demo paketleri oluşturuldu!")
        print("\nDemo repository'yi kullanmak için:")
        print("  python lpm_cli.py add-repo demo-repo file://$(pwd)/demo_repo")
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        sys.exit(1)
