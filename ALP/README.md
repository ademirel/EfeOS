# ALP - Advanced Linux Packager

Modern, fast, and reliable package manager for EfeOS.

## Features

### ✨ Core Features
- **Fast Dependency Resolution**: Intelligent dependency resolver
- **New Package Format**: `.alp` (YAML metadata + tar.gz)
- **Transaction Log**: All operations tracked
- **Checksum Verification**: SHA256 package security
- **Repository System**: Centralized package repository management
- **Automatic File Discovery**: No manual file listing needed - supports packages with thousands of files

### 🚀 Future Features
- Atomic updates and rollback support
- Parallel package download and installation
- Delta packages (bandwidth optimization)
- Source-based package compilation
- GUI interface (GTK/Qt)

## Installation

```bash
cd ALP
pip install -r requirements.txt
```

## Usage

### Basic Commands

**Note**: Run all commands from the `ALP/` directory:

```bash
cd ALP

# Install package
python alp_cli.py install <package_name>

# Remove package
python alp_cli.py remove <package_name>

# Search for package
python alp_cli.py search <search_term>

# List installed packages
python alp_cli.py list

# List all available packages
python alp_cli.py list --all

# Update repository indexes
python alp_cli.py update

# View transaction history
python alp_cli.py history

# Clean cache
python alp_cli.py clean
```

### Repository Management

```bash
# Add repository
python alp_cli.py add-repo <name> <url>

# List repositories
python alp_cli.py list-repos
```

## Package Format (.alp)

ALP uses its own custom package format:

**Structure:**
```
package-name-version.alp
├── metadata.yaml    # Package information
└── data.tar.gz      # Package contents
```

**metadata.yaml example:**
```yaml
name: example-package
version: 1.0.0
description: Example package
architecture: x86_64
dependencies:
  - gcc>=11.0
  - glibc>=2.35
conflicts: []
provides: []
maintainer: developer@example.com
homepage: https://example.com
license: GPL-3.0
size: 1048576
checksum: abc123...
files:
  - bin/example
  - lib/libexample.so
```

## Development

### Project Structure

```
ALP/
├── alp/                 # Python module
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # CLI commands
│   ├── database.py      # SQLite database
│   ├── resolver.py      # Dependency resolver
│   ├── package.py       # Package format handling
│   ├── repository.py    # Repository management
│   ├── downloader.py    # Download and verification
│   └── transaction.py   # Transaction log
├── tools/               # Utility tools
│   └── generate_repo_index.py
├── examples/            # Build system examples
├── demo_repo/           # Demo repository
├── alp_data/            # Runtime data
├── alp_cli.py           # Main entry point
├── test_alp.sh          # Test script
├── create_demo_package.py
├── requirements.txt     # Python dependencies
├── README.md
├── PACKAGE_GUIDE.md     # Detailed package management guide
└── ARCHITECTURE.md      # Architecture documentation
```

## Environment Variables

```bash
ALP_DB_PATH=/var/lib/alp/packages.db      # Database location
ALP_CACHE_DIR=/var/cache/alp              # Cache directory
ALP_LOG_DIR=/var/log/alp                  # Log directory
```

## Documentation

- **[PACKAGE_GUIDE.md](PACKAGE_GUIDE.md)**: Detailed guide for package creation, installation, updates, and removal
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture and design decisions
- **[examples/](examples/)**: Build examples for different build systems (CMake, Autotools, Cargo, etc.)

## Key Concepts

### DESTDIR-Based Packaging

ALP uses the DESTDIR approach for clean package creation:

1. **Compile source code**: `./configure && make` (or CMake, Meson, etc.)
2. **Install to staging**: `make install DESTDIR=/tmp/staging`
3. **Create package**: ALP automatically scans all files in staging directory
4. **No manual file listing**: Even packages with thousands of files are handled automatically

### Supported Build Systems

- ✅ Autotools (configure/make)
- ✅ CMake
- ✅ Meson/Ninja
- ✅ Cargo (Rust)
- ✅ Go
- ✅ Python (setuptools/poetry)
- ✅ Any build system supporting DESTDIR

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3).

For more information, see the [LICENSE](LICENSE) file or visit https://www.gnu.org/licenses/gpl-3.0.html

## Contributing

Contributions are welcome! Feel free to submit pull requests.
