# ALP Architecture Documentation

## Overview

ALP is a modular system designed with modern package management principles.

## Module Structure

### 1. Package (alp/package.py)
**Responsibility**: Package format and processing

- `.alp` format definition (YAML metadata + tar.gz data)
- Package creation and loading
- SHA256 checksum calculation and verification
- Package content extraction
- **Automatic file discovery** using `os.walk()`

**Key Classes**:
- `PackageMetadata`: Package metadata (dataclass)
- `Package`: Package processing class

**Key Methods**:
- `create_package()`: Creates .alp package, **automatically scans all files** in source directory
- `load_package()`: Loads existing .alp package
- `verify_checksum()`: Verifies package integrity

### 2. Database (alp/database.py)
**Responsibility**: Installed package state management

- SQLite-based package tracking
- Upgrade support (UPDATE OR INSERT)
- Dependency and file list storage
- Repository management

**Key Functions**:
- `add_package()`: Add new package or update existing
- `get_package()`: Get package info with full metadata (files, dependencies included)
- `remove_package()`: Remove package and associated data
- `is_package_installed()`: Check package installation status

**Tables**:
- `packages`: Main package information
- `dependencies`: Package dependencies
- `files`: Package file list
- `repositories`: Repository information

### 3. Resolver (alp/resolver.py)
**Responsibility**: Dependency resolution

- Version constraint tracking
- Dependency graph resolution
- Conflict detection
- Upgrade requirement detection

**Key Algorithms**:
- BFS-based dependency resolution
- Version comparison (semantic versioning)
- Re-evaluation mechanism (when stricter constraints arrive)

**Output Format**:
```python
{
    'install': [package list],
    'conflicts': [conflicting packages],
    'missing': [not found/incompatible packages]
}
```

### 4. Repository (alp/repository.py)
**Responsibility**: Package repository management

- Repository index updates (HTTP and file://)
- Package search
- Metadata queries
- Index caching

**Index Format**:
```json
{
  "name": "repo-name",
  "packages": [
    {
      "name": "pkg",
      "version": "1.0.0",
      "dependencies": ["dep>=1.0"],
      ...
    }
  ]
}
```

### 5. Downloader (alp/downloader.py)
**Responsibility**: Package download and verification

- HTTP and file:// protocol support
- Progress callback
- Checksum verification
- Cache management

**Security**:
- file:// path validation
- .alp extension check
- File existence verification

### 6. Transaction (alp/transaction.py)
**Responsibility**: Transaction logging system

- Transaction logging (append-only)
- Transaction state tracking
- Error handling (corrupted line skip)
- History management

**Transaction States**:
- PENDING
- IN_PROGRESS
- COMPLETED
- FAILED
- ROLLED_BACK

### 7. CLI (alp/cli.py)
**Responsibility**: User interface

- Command processing (install, remove, search, etc.)
- Snapshot-based rollback
- Progress display
- Error handling

**Rollback Mechanism**:
1. Snapshot of current packages taken at transaction start
2. Track failures during each package installation
3. On error:
   - Remove newly installed packages
   - Restore upgraded packages to old version
   - Clean downloaded files

## Data Flow

### Package Installation
```
User Request
    ↓
CLI (install command)
    ↓
Resolver (dependency resolution)
    ↓
Repository (package metadata)
    ↓
Downloader (download package)
    ↓
Package (verify checksum)
    ↓
Database (save metadata)
    ↓
Transaction (log success)
```

### Error Rollback Flow
```
Installation Error
    ↓
CLI Rollback Handler
    ├→ Remove newly installed packages
    ├→ Restore upgraded packages (snapshot)
    └→ Clean downloaded files
    ↓
Transaction (log failure)
```

## Package Creation Workflow

### Traditional Package Managers (Manual File Listing)
```
Source Code
    ↓
Compile
    ↓
Manual file listing (tedious for thousands of files!)
    ↓
Create package spec
    ↓
Build package
```

### ALP Approach (Automatic Discovery)
```
Source Code
    ↓
Compile (cmake/autotools/meson/cargo/etc.)
    ↓
Install to DESTDIR staging directory
    ↓
ALP automatically scans ALL files (os.walk)
    ↓
Create .alp package (no manual listing!)
```

**Example**:
```python
# Even with 10,000 files, no manual listing needed!
pkg = Package.create_package(
    name='gcc',
    version='11.2.0',
    source_dir='/tmp/gcc-staging',  # Contains all compiled files
    output_path='gcc-11.2.0',
    metadata_dict=metadata
)
# ALP automatically discovers all 10,000 files!
```

## Design Principles

### 1. Separation of Concerns
Each module has a single responsibility and can be independently tested.

### 2. Error Recovery
Rollback mechanism available for all critical operations.

### 3. Data Integrity
- Checksum verification
- Transaction logging
- Database ACID properties

### 4. Security
- Path validation
- File type checking
- No arbitrary code execution

### 5. Extensibility
- Plugin-ready architecture
- Repository system
- Modular design

### 6. Automatic File Discovery
- No manual file listing required
- Works with packages containing thousands of files
- Clean DESTDIR-based workflow
- Supports any build system (CMake, Autotools, Meson, Cargo, Go, etc.)

## Build System Support

ALP supports any build system through the DESTDIR pattern:

### Autotools
```bash
./configure --prefix=/usr
make
make install DESTDIR=/tmp/staging
```

### CMake
```bash
cmake . -DCMAKE_INSTALL_PREFIX=/usr
make
make install DESTDIR=/tmp/staging
```

### Meson
```bash
meson setup build --prefix=/usr
ninja -C build
DESTDIR=/tmp/staging ninja -C build install
```

### Cargo (Rust)
```bash
cargo build --release
# Manual staging for Rust
mkdir -p /tmp/staging/usr/bin
cp target/release/myapp /tmp/staging/usr/bin/
```

### Go
```bash
go build -o myapp
mkdir -p /tmp/staging/usr/bin
cp myapp /tmp/staging/usr/bin/
```

**All of these** feed into the same ALP packaging process:
```python
pkg = Package.create_package(
    name='myapp',
    version='1.0.0',
    source_dir='/tmp/staging',
    output_path='myapp-1.0.0',
    metadata_dict=metadata
)
```

## Future Enhancements

### Priority 1: Core Improvements
- Parallel package download
- Atomic upgrades (system snapshot)
- Delta packages

### Priority 2: Advanced Features
- Source-based package compilation
- Package signing (GPG)
- Dependency conflict resolution improvements

### Priority 3: UI/UX
- GUI (GTK/Qt)
- TUI (ncurses)
- Web interface

## Test Strategy

### Unit Tests (Recommended)
- Package creation/verification
- Version comparison
- Dependency resolution
- Database operations
- Automatic file discovery

### Integration Tests (Recommended)
- Full install/remove cycle
- Upgrade scenarios
- Rollback functionality
- Conflict detection
- Large package handling (1000+ files)

### Regression Tests (Critical)
- Upgrade rollback (snapshot restore)
- Version constraint enforcement
- file:// validation
- Transaction log corruption handling
- Automatic file scanning with various directory structures

## Key Differentiators

### vs DNF/YUM
- ✅ Faster dependency resolution
- ✅ Cleaner package format (YAML + tar.gz)
- ✅ Built-in rollback mechanism
- ✅ Automatic file discovery (no manual .spec file maintenance)

### vs APT/DPKG
- ✅ Simpler package creation workflow
- ✅ No manual file listing in control files
- ✅ DESTDIR-based staging (cleaner build process)
- ✅ Transaction logging

### vs Pacman
- ✅ Automatic file discovery
- ✅ Python-based (easier to extend)
- ✅ Built-in repository index generation tool

## License

GPLv3 - See LICENSE file for details.
