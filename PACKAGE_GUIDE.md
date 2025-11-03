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

### Package Structure

ALP packages use the `.alp` format, which combines a YAML metadata file with a tar.gz archive of files.

### Step 1: Prepare Your Files

Organize your files in a directory structure:

```
my-package/
├── usr/
│   ├── bin/
│   │   └── myapp
│   └── lib/
│       └── libmyapp.so
└── etc/
    └── myapp.conf
```

### Step 2: Create Package Metadata

Create a Python script to generate your package:

```python
#!/usr/bin/env python3
from alp.package import Package

metadata = {
    'description': 'My awesome application',
    'architecture': 'x86_64',
    'dependencies': ['glibc>=2.35.0'],
    'conflicts': [],
    'provides': ['myapp'],
    'maintainer': 'you@example.com',
    'homepage': 'https://example.com/myapp',
    'license': 'MIT'
}

pkg = Package.create_package(
    name='myapp',
    version='1.0.0',
    source_dir='my-package',
    output_path='myapp-1.0.0',
    metadata_dict=metadata
)

print(f"Package created: {pkg}")
print(f"Checksum: {pkg.metadata.checksum}")
```

### Step 3: Create Repository Index

Create an `index.json` file for your repository:

```json
{
  "name": "my-repo",
  "description": "My Package Repository",
  "version": "1.0",
  "packages": [
    {
      "name": "myapp",
      "version": "1.0.0",
      "description": "My awesome application",
      "architecture": "x86_64",
      "dependencies": ["glibc>=2.35.0"],
      "conflicts": [],
      "provides": ["myapp"],
      "maintainer": "you@example.com",
      "homepage": "https://example.com/myapp",
      "license": "MIT",
      "size": 16384,
      "checksum": "your_package_checksum_here",
      "files": ["usr/bin/myapp", "usr/lib/libmyapp.so", "etc/myapp.conf"]
    }
  ]
}
```

### Repository Directory Structure

```
my-repo/
├── index.json
└── packages/
    └── myapp-1.0.0.alp
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

## Examples

### Complete Workflow Example

```bash
# 1. Add a repository
python alp_cli.py add-repo my-repo "https://repo.example.com"

# 2. Update repository indexes
python alp_cli.py update

# 3. Search for a package
python alp_cli.py search webserver

# 4. Install a package with dependencies
python alp_cli.py install nginx

# 5. List installed packages
python alp_cli.py list

# 6. View transaction history
python alp_cli.py history

# 7. Remove a package
python alp_cli.py remove nginx

# 8. Clean cache
python alp_cli.py clean
```

### Creating and Using a Local Repository

```bash
# 1. Create your packages
python create_my_packages.py

# 2. Set up repository structure
mkdir -p my-repo/packages
mv *.alp my-repo/packages/
cp index.json my-repo/

# 3. Add the repository
python alp_cli.py add-repo local "file://$(pwd)/my-repo"

# 4. Update and install
python alp_cli.py update
python alp_cli.py install my-package
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

---

## Best Practices

1. **Always Update First**: Run `python alp_cli.py update` before installing packages
2. **Check Dependencies**: Use `python alp_cli.py search` to verify package availability
3. **Review Transaction History**: Monitor installations with `python alp_cli.py history`
4. **Clean Regularly**: Free up space with `python alp_cli.py clean`
5. **Use Version Pinning**: Specify exact versions in dependencies when needed
6. **Test in Isolation**: Test new packages before deploying to production
7. **Backup Database**: Keep backups of your package database before major changes

---

## License

ALP is licensed under GPLv3. See LICENSE file for details.
