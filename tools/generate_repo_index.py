#!/usr/bin/env python3
"""
Automatic repository index generator
Scans .alp packages and creates index.json
"""
import json
import os
import sys
from alp.package import Package


def generate_repo_index(packages_dir, repo_name, repo_description, output_path=None):
    """
    Scan packages directory and automatically generate index.json
    
    Args:
        packages_dir: Directory containing .alp packages
        repo_name: Repository name
        repo_description: Repository description
        output_path: Optional custom output path for index.json
    """
    
    if not os.path.exists(packages_dir):
        print(f"❌ Error: Directory not found: {packages_dir}")
        sys.exit(1)
    
    packages = []
    
    print(f"📦 Scanning packages in: {packages_dir}")
    
    # Find all .alp files
    alp_files = [f for f in os.listdir(packages_dir) if f.endswith('.alp')]
    
    if not alp_files:
        print(f"⚠️  Warning: No .alp files found in {packages_dir}")
    
    for filename in sorted(alp_files):
        pkg_path = os.path.join(packages_dir, filename)
        
        try:
            # Load package metadata
            print(f"  📄 Loading {filename}...")
            pkg = Package.load_package(pkg_path)
            meta = pkg.metadata
            
            # Add to packages list
            package_info = {
                'name': meta.name,
                'version': meta.version,
                'description': meta.description,
                'architecture': meta.architecture,
                'dependencies': meta.dependencies,
                'conflicts': meta.conflicts,
                'provides': meta.provides,
                'maintainer': meta.maintainer,
                'homepage': meta.homepage,
                'license': meta.license,
                'size': meta.size,
                'checksum': meta.checksum,
                'files': meta.files  # Automatically included from package scan
            }
            
            packages.append(package_info)
            
            print(f"    ✅ {meta.name}-{meta.version}")
            print(f"       Files: {len(meta.files)}")
            print(f"       Size: {meta.size / (1024*1024):.2f} MB")
            
        except Exception as e:
            print(f"    ❌ Error loading {filename}: {e}")
            continue
    
    # Create index
    index = {
        'name': repo_name,
        'description': repo_description,
        'version': '1.0',
        'packages': packages
    }
    
    # Determine output path
    if output_path is None:
        output_path = os.path.join(os.path.dirname(packages_dir), 'index.json')
    
    # Write index.json
    with open(output_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"\n✅ Repository index generated: {output_path}")
    print(f"   Repository: {repo_name}")
    print(f"   Packages: {len(packages)}")
    print(f"\n📋 Package Summary:")
    for pkg in packages:
        print(f"   - {pkg['name']}-{pkg['version']}: {len(pkg['files'])} files, {pkg['size'] / (1024*1024):.2f} MB")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ALP repository index from .alp packages')
    parser.add_argument('packages_dir', help='Directory containing .alp packages')
    parser.add_argument('--name', default='custom-repo', help='Repository name')
    parser.add_argument('--description', default='Custom ALP Repository', help='Repository description')
    parser.add_argument('--output', help='Output path for index.json (default: <repo_dir>/index.json)')
    
    args = parser.parse_args()
    
    generate_repo_index(
        packages_dir=args.packages_dir,
        repo_name=args.name,
        repo_description=args.description,
        output_path=args.output
    )
