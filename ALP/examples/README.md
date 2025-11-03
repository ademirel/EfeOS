# ALP Build Examples

This directory contains example scripts for building packages with different build systems.

## Available Examples

### 1. `build_alp_itself.sh`
**Meta-packaging**: Package ALP using ALP itself!

```bash
bash examples/build_alp_itself.sh
```

This demonstrates how to:
- Install Python modules to `/usr/lib/python3/site-packages`
- Create executable scripts in `/usr/bin`
- Include documentation
- Package everything into `.alp` format

### 2. `build_cmake_package.sh`
Build and package CMake-based applications.

```bash
bash examples/build_cmake_package.sh
```

Shows how to:
- Configure with CMake
- Build with make
- Install to DESTDIR staging directory
- Create ALP package

### 3. `build_any_source.sh`
Universal builder supporting multiple build systems.

```bash
# Autotools
bash examples/build_any_source.sh myapp 1.0.0 autotools /path/to/source

# CMake
bash examples/build_any_source.sh myapp 1.0.0 cmake /path/to/source

# Meson
bash examples/build_any_source.sh myapp 1.0.0 meson /path/to/source

# Cargo (Rust)
bash examples/build_any_source.sh myapp 1.0.0 cargo /path/to/source

# Go
bash examples/build_any_source.sh myapp 1.0.0 go /path/to/source
```

## Key Concept: DESTDIR

All build systems use **DESTDIR** to install to a staging directory:

```bash
# Autotools
make install DESTDIR=/tmp/staging

# CMake
make install DESTDIR=/tmp/staging

# Meson
DESTDIR=/tmp/staging ninja install
```

This allows ALP to:
1. Scan all installed files automatically
2. Create package without manual file listing
3. Keep system clean (no direct /usr installation during packaging)

## Package Creation Flow

```
Source Code
    ↓
Configure (cmake/autotools/etc)
    ↓
Compile (make/ninja/cargo/etc)
    ↓
Install to DESTDIR staging
    ↓
ALP scans staging directory (automatic)
    ↓
Create .alp package
```

## Example: Packaging a Real Application

Let's say you want to package `htop`:

```bash
# 1. Download source
wget https://github.com/htop-dev/htop/archive/3.2.1.tar.gz
tar xzf 3.2.1.tar.gz
cd htop-3.2.1

# 2. Build
./autogen.sh
./configure --prefix=/usr
make

# 3. Install to staging
STAGING=/tmp/htop-staging
make install DESTDIR=$STAGING

# 4. Create ALP package
cd /path/to/ALP
python3 << EOF
from alp.package import Package

metadata = {
    'description': 'Interactive process viewer',
    'architecture': 'x86_64',
    'dependencies': ['ncurses>=6.0'],
    'conflicts': [],
    'provides': ['htop'],
    'maintainer': 'you@example.com',
    'homepage': 'https://htop.dev',
    'license': 'GPL-2.0'
}

pkg = Package.create_package(
    name='htop',
    version='3.2.1',
    source_dir='$STAGING',
    output_path='htop-3.2.1',
    metadata_dict=metadata
)

print(f"Created: {pkg}")
print(f"Files: {len(pkg.metadata.files)}")
EOF
```

Done! You now have `htop-3.2.1.alp` ready to distribute.
