#!/usr/bin/env python3
"""
Demo package creation script
Creates example packages in ALP format
"""

import os
import sys
from alp.package import Package, PackageMetadata

def create_hello_world_package():
    """Create Hello World package"""
    
    os.makedirs("demo_packages/hello-world/usr/bin", exist_ok=True)
    
    with open("demo_packages/hello-world/usr/bin/hello", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("echo 'Hello, World from ALP!'\n")
    
    os.chmod("demo_packages/hello-world/usr/bin/hello", 0o755)
    
    metadata = {
        'description': 'Simple Hello World application',
        'architecture': 'x86_64',
        'dependencies': [],
        'conflicts': [],
        'provides': ['hello'],
        'maintainer': 'demo@alp.local',
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
    
    print(f"✅ {pkg} created")
    print(f"   Checksum: {pkg.metadata.checksum}")
    print(f"   Size: {pkg.metadata.size} bytes")

def create_example_lib_package():
    """Create Example Library package"""
    
    os.makedirs("demo_packages/example-lib/usr/lib", exist_ok=True)
    
    with open("demo_packages/example-lib/usr/lib/libexample.so", "w") as f:
        f.write("// Example library binary file\n")
        f.write("void example_function() { return; }\n")
    
    metadata = {
        'description': 'Example library package',
        'architecture': 'x86_64',
        'dependencies': [],
        'conflicts': [],
        'provides': ['libexample'],
        'maintainer': 'demo@alp.local',
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
    
    print(f"✅ {pkg} created")
    print(f"   Checksum: {pkg.metadata.checksum}")
    print(f"   Size: {pkg.metadata.size} bytes")

if __name__ == '__main__':
    print("📦 Creating demo packages...\n")
    
    try:
        create_hello_world_package()
        print()
        create_example_lib_package()
        print("\n✅ All demo packages created!")
        print("\nTo use the demo repository:")
        print("  python alp_cli.py add-repo demo-repo file://$(pwd)/demo_repo")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
