# CMake Application Packaging Example

This guide demonstrates how to package an application built with CMake.

## Example: htop (Uses CMake)

### 1. Download and Compile Source Code

```bash
# Download source code
wget https://github.com/htop-dev/htop/archive/refs/tags/3.3.0.tar.gz
tar xzf 3.3.0.tar.gz
cd htop-3.3.0

# Create CMake build directory
mkdir build
cd build

# Configure (prefix is important!)
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr

# Compile (parallel)
make -j$(nproc)
```

### 2. Install to DESTDIR (Critical Step!)

```bash
# Create staging directory
STAGING=/tmp/htop-staging
rm -rf $STAGING

# Install to staging with DESTDIR (not to system!)
make install DESTDIR=$STAGING

# Verify
tree $STAGING  # or: find $STAGING
```

**Example output:**
```
/tmp/htop-staging/
└── usr/
    ├── bin/
    │   └── htop
    ├── share/
    │   ├── applications/
    │   │   └── htop.desktop
    │   ├── icons/
    │   │   └── hicolor/scalable/apps/htop.svg
    │   ├── man/
    │   │   └── man1/
    │   │       └── htop.1
    │   └── pixmaps/
    │       └── htop.png
    └── lib/
        └── systemd/
```

### 3. Create ALP Package

```bash
cd /path/to/ALP

python3 << 'EOF'
from alp.package import Package

metadata = {
    'description': 'Interactive process viewer for Unix systems',
    'architecture': 'x86_64',
    'dependencies': [
        'ncurses>=6.0',
        'glibc>=2.35.0'
    ],
    'conflicts': [],
    'provides': ['htop', 'process-viewer'],
    'maintainer': 'packager@example.com',
    'homepage': 'https://htop.dev',
    'license': 'GPL-2.0'
}

# Automatically scans ALL files!
pkg = Package.create_package(
    name='htop',
    version='3.3.0',
    source_dir='/tmp/htop-staging',
    output_path='htop-3.3.0',
    metadata_dict=metadata
)

print(f"✅ Package created: {pkg}")
print(f"   Total files: {len(pkg.metadata.files)}")
print(f"   Size: {pkg.metadata.size / (1024*1024):.2f} MB")
print(f"\n📋 Discovered files:")
for f in pkg.metadata.files:
    print(f"   - {f}")
EOF
```

### 4. Add to Repository

```bash
# Move package to repository
mv htop-3.3.0.alp my-repo/packages/

# Update repository index
python tools/generate_repo_index.py my-repo/packages \
    --name "my-repo" \
    --description "My Custom Repository"
```

### 5. Install and Test

```bash
# Add repository
python alp_cli.py add-repo my-repo "file://$(pwd)/my-repo"

# Update index
python alp_cli.py update

# Install package
python alp_cli.py install htop

# Test
htop --version
```

## Other CMake Examples

### Using Ninja build system

```bash
cmake -G Ninja .. -DCMAKE_INSTALL_PREFIX=/usr
ninja
DESTDIR=/tmp/staging ninja install
```

### Cross-compilation

```bash
cmake .. \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_TOOLCHAIN_FILE=/path/to/toolchain.cmake
make
make install DESTDIR=/tmp/staging-arm64
```

### Creating debug package

```bash
cmake .. \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_INSTALL_PREFIX=/usr
make
make install DESTDIR=/tmp/staging-debug

# Create package with debug symbols
pkg = Package.create_package(
    name='htop-debug',
    version='3.3.0',
    source_dir='/tmp/staging-debug',
    output_path='htop-debug-3.3.0',
    metadata_dict={
        'description': 'htop with debug symbols',
        ...
    }
)
```

## Important Notes

1. **Always use DESTDIR** - Never install directly to system!
2. **PREFIX should be /usr** - So package installs to correct location
3. **ALP scans automatically** - No manual file listing needed
4. **Add dependencies** - Write libraries found by CMake to dependencies

## Troubleshooting

### DESTDIR not working?

Some old CMake projects may not support DESTDIR. Solution:

```bash
# Set install prefix as staging directory
cmake .. -DCMAKE_INSTALL_PREFIX=/tmp/staging/usr
make install

# Adjust path when creating package
pkg = Package.create_package(
    name='myapp',
    version='1.0.0',
    source_dir='/tmp/staging',  # Contains usr/
    ...
)
```

### Files not found?

```bash
# Check staging directory
find /tmp/staging -type f

# If empty, examine make install logs
make install VERBOSE=1 DESTDIR=/tmp/staging
```

## Conclusion

With the CMake → DESTDIR → ALP packaging workflow:
- ✅ Thousands of files are automatically discovered
- ✅ No manual file listing required
- ✅ System stays clean
- ✅ You create professional packages
