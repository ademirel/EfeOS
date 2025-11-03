# ALP - Advanced Linux Packager

## Project Overview
Modern, advanced package manager for LFS (Linux From Scratch) based Linux distributions.

## Target Features
- **Fast dependency resolution**: Advanced dependency resolver
- **Parallel operations**: Multi-package download and installation
- **Atomic updates**: Rollback support
- **Transaction log**: All operations tracked
- **New package format**: .alp (Advanced Linux Package) format

## Current Status
- ✅ MVP completed and production-ready
- CLI tool fully functional (GUI in next phase)
- All critical bugs fixed and architect approved
- ✅ All project files organized under ALP/ main folder
- ✅ Full English localization (all user-facing text)

## Project Structure
```
ALP/
├── alp/              - Main package module
│   ├── cli.py        - CLI commands (install, remove, update, search, list)
│   ├── database.py   - SQLite database management
│   ├── resolver.py   - Dependency resolver
│   ├── package.py    - Package format handling (automatic file scanning)
│   ├── repository.py - Repository management
│   ├── downloader.py - Download and verification
│   └── transaction.py- Transaction log system
├── tools/            - Utility tools
│   └── generate_repo_index.py - Automatic repo index generation
├── examples/         - Build system examples (CMake, Autotools, etc.)
├── demo_repo/        - Demo repository with packages
├── alp_data/         - Runtime data (database, cache, logs)
├── alp_cli.py        - Main CLI entry point
├── test_alp.sh       - Test script
├── create_demo_package.py - Demo package creation
├── README.md         - English usage guide
├── PACKAGE_GUIDE.md  - English detailed package management guide
├── ARCHITECTURE.md   - English architecture documentation
└── LICENSE           - GPLv3 license
```

## Package Format (.alp)
YAML metadata + tar.gz archive combination
- Metadata: Dependencies, version, checksums, **automatic file list**
- Content: Binary/source files

## Technical Details

### Security Features
- SHA256 checksum verification
- file:// path validation (.alp extension check)
- Transaction log with audit trail

### Features
- ✅ Fast dependency resolution (version constraint enforcement)
- ✅ Upgrade support (in-place update)
- ✅ Snapshot-based rollback (restore old version on upgrade)
- ✅ Transaction logging (with error handling)
- ✅ Repository management (file:// and HTTP support)
- ✅ Checksum verification
- ✅ Conflict detection
- ✅ **Automatic file scanning** - No manual file listing needed for thousands of files!

### Package Creation Workflow
1. **Compile source code**: `./configure && make` (or CMake, Meson, Cargo, etc.)
2. **Install to DESTDIR**: `make install DESTDIR=/tmp/staging`
3. **Create ALP package**: `Package.create_package()` automatically scans all files
4. **Generate repository index**: Automatic with `tools/generate_repo_index.py`

### Supported Build Systems
- Autotools (configure/make)
- CMake
- Meson/Ninja
- Cargo (Rust)
- Go
- Python (setuptools/poetry)
- Any system supporting DESTDIR

### Future Enhancements (Recommended)
- Parallel package download
- Atomic updates
- Delta packages
- Source-based package compilation
- GUI interface (GTK/Qt)
- Test coverage (regression tests)

## Recent Changes
- 2025-11-03: Project reorganization
  - All files and folders organized under ALP/ main folder
  - PACKAGE_GUIDE.md updated: automatic file scanning explained
  - tools/generate_repo_index.py added: automatic repo index generation
  - Paths and workflow updated for new structure
  - Added examples/ directory with build system examples

- 2025-11-03: MVP completed
  - Critical bugs fixed (dependency version enforcement, upgrade rollback, file validation)
  - Database upgrade support added
  - Snapshot-based rollback implementation
  - Transaction log error handling
  - Production-ready status achieved
  - Full English localization (all user-facing text)

## Usage
```bash
# Navigate to ALP directory
cd ALP

# Add demo repository
python alp_cli.py add-repo demo-repo "file://$(pwd)/demo_repo"

# Update repository indexes
python alp_cli.py update

# Search for package
python alp_cli.py search hello

# Install package
python alp_cli.py install hello-world
```

## Key Advantages

### Automatic File Discovery
Unlike traditional package managers that require manual file listing, ALP automatically discovers all files in the staging directory using `os.walk()`. This means:
- ✅ Packages with thousands of files are handled automatically
- ✅ No manual maintenance of file lists
- ✅ Clean, DESTDIR-based workflow
- ✅ Works with any build system

### Example: Self-Packaging
ALP can package itself using ALP! This demonstrates the meta-packaging capability:

```bash
# Build ALP package using ALP itself
cd ALP
python3 << 'EOF'
from alp.package import Package
pkg = Package.create_package(
    name='alp',
    version='0.1.0',
    source_dir='/tmp/alp-staging',  # Contains all installed files
    output_path='alp-0.1.0',
    metadata_dict={...}
)
# Result: alp-0.1.0.alp (20 files automatically discovered)
EOF
```

## License
GPLv3 - See LICENSE file for details.
