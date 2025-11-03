# ALP Package Management Guide

This guide covers the essential operations for managing packages with ALP (Advanced Linux Packager).

## Table of Contents

- [Creating a New Package](#creating-a-new-package)
- [Installing Packages](#installing-packages)
- [Updating Repository Indexes](#updating-repository-indexes)
- [Removing Packages](#removing-packages)
- [Managing Repositories](#managing-repositories)
- [Additional Commands](#additional-commands)

---

## Creating a New Package

### Overview

Creating an ALP package involves three main steps:
1. **Download and compile** the source code
2. **Install to a staging directory** using DESTDIR
3. **Create the .alp package** (ALP automatically scans all files)

### Step 1: Download and Compile Source

Download and build your software from source:

```bash
# Example: Building hello-world application
wget https://example.com/hello-world-1.0.0.tar.gz
tar xzf hello-world-1.0.0.tar.gz
cd hello-world-1.0.0

# Configure and compile
./configure --prefix=/usr
make
```

### Step 2: Install to Staging Directory

**Important**: Never install directly to `/usr`! Use `DESTDIR` to install to a temporary directory:

```bash
# Create staging directory
mkdir -p /tmp/hello-world-package

# Install to staging directory (DESTDIR method)
make install DESTDIR=/tmp/hello-world-package

# Now /tmp/hello-world-package contains the organized structure:
# /tmp/hello-world-package/
#   └── usr/
#       ├── bin/
#       │   └── hello
#       ├── lib/
#       │   └── libhello.so.1.0.0
#       ├── share/
#       │   ├── man/
#       │   │   └── man1/
#       │   │       └── hello.1
#       │   └── doc/
#       │       └── hello/
#       │           └── README
#       └── include/
#           └── hello.h
```

### Step 3: Create ALP Package

**Key Feature**: ALP automatically discovers ALL files in the staging directory - you don't need to list them manually!

```python
#!/usr/bin/env python3
from alp.package import Package

# Define metadata (NO file list needed!)
metadata = {
    'description': 'Hello World application with libraries',
    'architecture': 'x86_64',
    'dependencies': ['glibc>=2.35.0'],
    'conflicts': [],
    'provides': ['hello'],
    'maintainer': 'you@example.com',
    'homepage': 'https://example.com/hello-world',
    'license': 'MIT'
}

# Create package - automatically scans ALL files in staging directory
pkg = Package.create_package(
    name='hello-world',
    version='1.0.0',
    source_dir='/tmp/hello-world-package',  # Staging directory
    output_path='hello-world-1.0.0',
    metadata_dict=metadata
)

print(f"✅ Package created: {pkg}")
print(f"   Checksum: {pkg.metadata.checksum}")
print(f"   Size: {pkg.metadata.size} bytes")
print(f"   Files: {len(pkg.metadata.files)} files automatically discovered")

# The package file list is in pkg.metadata.files
for f in pkg.metadata.files:
    print(f"     - {f}")
```

**What happens automatically**:
- ✅ Recursively scans `/tmp/hello-world-package`
- ✅ Finds ALL files (binaries, libraries, configs, docs, etc.)
- ✅ Creates file list automatically
- ✅ Calculates package size
- ✅ Generates SHA-256 checksum
- ✅ Creates `hello-world-1.0.0.alp` package

### Step 4: Generate Repository Index

Create a script to automatically generate `index.json`:

```python
#!/usr/bin/env python3
"""
Generate repository index from .alp packages
"""
import json
import os
from alp.package import Package

def generate_repo_index(packages_dir, repo_name, repo_description):
    """Scan packages directory and generate index.json"""
    
    packages = []
    
    # Find all .alp files
    for filename in os.listdir(packages_dir):
        if filename.endswith('.alp'):
            pkg_path = os.path.join(packages_dir, filename)
            
            # Load package metadata
            pkg = Package.load_package(pkg_path)
            meta = pkg.metadata
            
            # Add to packages list
            packages.append({
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
                'files': meta.files  # Automatically included
            })
    
    # Create index
    index = {
        'name': repo_name,
        'description': repo_description,
        'version': '1.0',
        'packages': packages
    }
    
    # Write index.json
    index_path = os.path.join(os.path.dirname(packages_dir), 'index.json')
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"✅ Repository index generated: {index_path}")
    print(f"   Packages: {len(packages)}")
    for pkg in packages:
        print(f"     - {pkg['name']}-{pkg['version']} ({len(pkg['files'])} files)")

# Usage
generate_repo_index(
    packages_dir='my-repo/packages',
    repo_name='my-repo',
    repo_description='My Package Repository'
)
```

### Complete Example: Building GCC Package

Here's a real-world example for a large package with thousands of files:

```bash
#!/bin/bash
# build_gcc_package.sh

set -e

# 1. Download and extract
wget https://ftp.gnu.org/gnu/gcc/gcc-11.2.0/gcc-11.2.0.tar.gz
tar xzf gcc-11.2.0.tar.gz
cd gcc-11.2.0

# 2. Configure
mkdir build && cd build
../configure --prefix=/usr \
             --enable-languages=c,c++ \
             --disable-multilib

# 3. Compile (this may take hours!)
make -j$(nproc)

# 4. Install to staging directory
STAGING_DIR="/tmp/gcc-package"
rm -rf "$STAGING_DIR"
make install DESTDIR="$STAGING_DIR"

# 5. Create ALP package with Python
cd /path/to/packaging
python3 << 'EOF'
from alp.package import Package

metadata = {
    'description': 'GNU Compiler Collection',
    'architecture': 'x86_64',
    'dependencies': ['glibc>=2.35.0', 'binutils>=2.38'],
    'conflicts': [],
    'provides': ['gcc', 'g++', 'cc', 'c++'],
    'maintainer': 'packager@example.com',
    'homepage': 'https://gcc.gnu.org',
    'license': 'GPL-3.0'
}

# Automatically discovers ALL files (thousands of them!)
pkg = Package.create_package(
    name='gcc',
    version='11.2.0',
    source_dir='/tmp/gcc-package',
    output_path='gcc-11.2.0',
    metadata_dict=metadata
)

print(f"Package created with {len(pkg.metadata.files)} files")
# No need to list files manually!
EOF

echo "✅ GCC package created successfully"
```

### Directory Structure Best Practices

Follow the Filesystem Hierarchy Standard (FHS):

```
staging-dir/
├── usr/
│   ├── bin/          # User binaries
│   ├── sbin/         # System binaries
│   ├── lib/          # Libraries
│   ├── lib64/        # 64-bit libraries
│   ├── include/      # Header files
│   ├── share/        # Architecture-independent data
│   │   ├── man/      # Manual pages
│   │   ├── doc/      # Documentation
│   │   ├── info/     # Info pages
│   │   └── locale/   # Localization files
│   └── src/          # Source code
├── etc/              # Configuration files
├── var/              # Variable data
│   ├── lib/          # State information
│   └── log/          # Log files
└── opt/              # Optional packages
```

---

## Installing Packages

### Basic Installation

Install a single package:

```bash
python alp_cli.py install myapp
```

### Install Multiple Packages

```bash
python alp_cli.py install package1 package2 package3
```

### Install Without Dependencies

Skip dependency resolution:

```bash
python alp_cli.py install myapp --no-deps
```

### Auto-Confirm Installation

Skip confirmation prompt:

```bash
python alp_cli.py install myapp --yes
# or
python alp_cli.py install myapp -y
```

### Installation Process

1. **Dependency Resolution**: ALP automatically resolves and includes all dependencies
2. **Download**: Packages are downloaded to the cache directory
3. **Checksum Verification**: Package integrity is verified using SHA-256
4. **Installation**: Package is registered in the database and files are tracked
5. **Transaction Logging**: All actions are logged for rollback capability

### Installation with Rollback

If any package in the transaction fails, ALP automatically:
- Rolls back newly installed packages
- Restores previous versions of upgraded packages
- Cleans up downloaded files

---

## Updating Repository Indexes

### Update All Repositories

Refresh package indexes from all configured repositories:

```bash
python alp_cli.py update
```

This command:
- Fetches the latest `index.json` from each repository
- Updates the local cache with new package metadata
- Reports success or failure for each repository

### Best Practices

- Run `update` regularly to see the latest available packages
- Update before searching for or installing new packages
- Update after adding a new repository

---

## Removing Packages

### Basic Removal

Remove a single package:

```bash
python alp_cli.py remove myapp
```

### Remove Multiple Packages

```bash
python alp_cli.py remove package1 package2 package3
```

### Auto-Confirm Removal

Skip confirmation prompt:

```bash
python alp_cli.py remove myapp --yes
# or
python alp_cli.py remove myapp -y
```

### Dependency Protection

ALP prevents removal of packages that are dependencies of other installed packages:

```bash
$ python alp_cli.py remove glibc
❌ glibc cannot be removed. Dependent packages:
  - myapp
  - gcc
```

### Removal Process

1. **Dependency Check**: Verifies no other packages depend on it
2. **Confirmation**: Prompts for confirmation (unless `-y` flag used)
3. **Database Update**: Removes package from installed packages database
4. **Transaction Logging**: Logs the removal for history tracking

---

## Managing Repositories

### Add a Repository

```bash
python alp_cli.py add-repo <name> <url>
```

Examples:

```bash
# Add a local repository
python alp_cli.py add-repo local-repo "file:///path/to/repo"

# Add a remote repository
python alp_cli.py add-repo official-repo "https://packages.example.com/alp"

# Add with custom priority (higher = preferred)
python alp_cli.py add-repo priority-repo "https://example.com" --priority 200
```

### List Repositories

```bash
python alp_cli.py list-repos
```

Output:
```
📚 Repositories:

• official-repo
  URL: https://packages.example.com/alp
  Priority: 100

• local-repo
  URL: file:///path/to/repo
  Priority: 100
```

### Repository Priority

When multiple repositories provide the same package, ALP uses the repository with the highest priority value.

---

## Additional Commands

### Search for Packages

Search by name or description:

```bash
python alp_cli.py search <query>
```

Example:
```bash
$ python alp_cli.py search compiler
🔍 Searching for 'compiler'...

2 package(s) found:

[✓] gcc-11.2.0
    GNU Compiler Collection
    Repository: official-repo

[ ] clang-14.0.0
    LLVM C/C++ Compiler
    Repository: official-repo
```

Legend:
- `[✓]` = Installed
- `[ ]` = Not installed

### List Packages

List installed packages:

```bash
python alp_cli.py list
```

List all available packages:

```bash
python alp_cli.py list --all
# or
python alp_cli.py list -a
```

### View Transaction History

```bash
python alp_cli.py history
```

Limit number of records:

```bash
python alp_cli.py history --limit 20
# or
python alp_cli.py history -l 20
```

Output:
```
📜 Transaction history:

✅ [2024-11-03T08:15:30] install
   Packages: myapp, example-lib
   
❌ [2024-11-03T08:10:15] install
   Packages: broken-package
   Error: Download failed: broken-package
   
✅ [2024-11-03T08:05:00] remove
   Packages: old-app
```

### Clean Package Cache

Remove downloaded package files from cache:

```bash
python alp_cli.py clean
```

This frees up disk space by deleting cached `.alp` files while keeping packages installed.

---

## Environment Variables

Customize ALP behavior with environment variables:

```bash
# Database location
export ALP_DB_PATH="/custom/path/packages.db"

# Package cache directory
export ALP_CACHE_DIR="/custom/path/cache"

# Transaction log directory
export ALP_LOG_DIR="/custom/path/logs"
```

---

## Advanced Packaging Tips

### Handling Large Packages

For packages with thousands of files (like GCC, LLVM, etc.):

1. **Use DESTDIR consistently**: Always install to a staging directory
2. **Verify installation**: Check that all necessary files are in staging
3. **Let ALP scan automatically**: No manual file listing needed
4. **Test the package**: Extract and verify before publishing

```bash
# After creating package, verify it
python3 << 'EOF'
from alp.package import Package

pkg = Package.load_package('gcc-11.2.0.alp')
print(f"Package: {pkg.metadata.name}-{pkg.metadata.version}")
print(f"Total files: {len(pkg.metadata.files)}")
print(f"Size: {pkg.metadata.size / (1024*1024):.2f} MB")
print(f"Checksum: {pkg.metadata.checksum}")

# Check important files
important_files = ['usr/bin/gcc', 'usr/bin/g++', 'usr/lib/gcc']
for f in important_files:
    found = any(f in path for path in pkg.metadata.files)
    status = "✅" if found else "❌"
    print(f"{status} {f}")
EOF
```

### Splitting Large Packages

For very large software, consider splitting into multiple packages:

```bash
# Example: Split GCC into multiple packages
# gcc-11.2.0.alp          (core compiler)
# gcc-doc-11.2.0.alp      (documentation)
# gcc-locales-11.2.0.alp  (translations)
# libstdc++-11.2.0.alp    (C++ standard library)

# Each can be created from filtered staging directories
```

### Build Automation Script

Save this as `build_and_package.sh`:

```bash
#!/bin/bash
# Automated package building script

PACKAGE_NAME="$1"
PACKAGE_VERSION="$2"
SOURCE_URL="$3"

if [ $# -ne 3 ]; then
    echo "Usage: $0 <name> <version> <source_url>"
    exit 1
fi

set -e

STAGING_DIR="/tmp/${PACKAGE_NAME}-staging"
BUILD_DIR="/tmp/${PACKAGE_NAME}-build"

# Clean previous builds
rm -rf "$STAGING_DIR" "$BUILD_DIR"

# Download and extract
cd /tmp
wget -O "${PACKAGE_NAME}.tar.gz" "$SOURCE_URL"
tar xzf "${PACKAGE_NAME}.tar.gz"
cd "${PACKAGE_NAME}-${PACKAGE_VERSION}"

# Configure and build
./configure --prefix=/usr
make -j$(nproc)

# Install to staging
make install DESTDIR="$STAGING_DIR"

# Create ALP package
python3 << EOF
from alp.package import Package

metadata = {
    'description': '${PACKAGE_NAME} application',
    'architecture': 'x86_64',
    'dependencies': [],
    'conflicts': [],
    'provides': ['${PACKAGE_NAME}'],
    'maintainer': 'auto-packager@example.com',
    'homepage': 'https://example.com',
    'license': 'Unknown'
}

pkg = Package.create_package(
    name='${PACKAGE_NAME}',
    version='${PACKAGE_VERSION}',
    source_dir='${STAGING_DIR}',
    output_path='${PACKAGE_NAME}-${PACKAGE_VERSION}',
    metadata_dict=metadata
)

print(f"✅ Created: {pkg}")
print(f"   Files: {len(pkg.metadata.files)}")
EOF

echo "✅ Package built successfully: ${PACKAGE_NAME}-${PACKAGE_VERSION}.alp"
```

---

## Troubleshooting

### Package Not Found

```bash
❌ Missing packages: myapp
```

**Solution**: Update repository indexes with `python alp_cli.py update`

### Dependency Conflicts

```bash
⚠️ Conflicting packages: package-a, package-b
```

**Solution**: Check package dependencies and remove conflicting packages first

### Download Failed

```bash
❌ myapp installation failed: Download failed: myapp
```

**Solutions**:
- Check network connectivity
- Verify repository URL is correct
- Ensure package exists in repository index

### Checksum Mismatch

```bash
❌ myapp installation failed: Checksum error: myapp
```

**Solution**: 
- Re-download the package with `python alp_cli.py clean` then retry
- Verify package integrity in the repository

### Too Many Files Error

If you have millions of files, consider:
- Splitting package into smaller sub-packages
- Excluding unnecessary files (temp files, build artifacts)
- Using compression more efficiently

---

## Best Practices

1. **Always Use DESTDIR**: Never install directly to system directories during packaging
2. **Automatic File Discovery**: Let ALP scan files - don't list them manually
3. **Verify Before Publishing**: Always test your packages before adding to repository
4. **Update First**: Run `python alp_cli.py update` before installing packages
5. **Check Dependencies**: Use `python alp_cli.py search` to verify package availability
6. **Review Transaction History**: Monitor installations with `python alp_cli.py history`
7. **Clean Regularly**: Free up space with `python alp_cli.py clean`
8. **Use Version Pinning**: Specify exact versions in dependencies when needed
9. **Split Large Packages**: Consider splitting documentation, locales, development files
10. **Automate Builds**: Use scripts for reproducible package builds

---

## License

ALP is licensed under GPLv3. See LICENSE file for details.
