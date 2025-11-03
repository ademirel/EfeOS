# CMake Uygulaması Paketleme Örneği

Bu belge CMake ile derlenen bir uygulamanın nasıl paketleneceğini gösterir.

## Örnek: htop (CMake kullanıyor)

### 1. Kaynak Kodu İndir ve Derle

```bash
# Kaynak kodu indir
wget https://github.com/htop-dev/htop/archive/refs/tags/3.3.0.tar.gz
tar xzf 3.3.0.tar.gz
cd htop-3.3.0

# CMake ile build dizini oluştur
mkdir build
cd build

# Configure (prefix önemli!)
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr

# Compile (parallel)
make -j$(nproc)
```

### 2. DESTDIR'e Kur (Kritik Adım!)

```bash
# Staging directory oluştur
STAGING=/tmp/htop-staging
rm -rf $STAGING

# DESTDIR ile staging'e kur (sisteme değil!)
make install DESTDIR=$STAGING

# Kontrol et
tree $STAGING  # veya: find $STAGING
```

**Çıktı örneği:**
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

### 3. ALP Paketi Oluştur

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

# Otomatik olarak TÜM dosyaları tarar!
pkg = Package.create_package(
    name='htop',
    version='3.3.0',
    source_dir='/tmp/htop-staging',
    output_path='htop-3.3.0',
    metadata_dict=metadata
)

print(f"✅ Paket oluşturuldu: {pkg}")
print(f"   Toplam dosya: {len(pkg.metadata.files)}")
print(f"   Boyut: {pkg.metadata.size / (1024*1024):.2f} MB")
print(f"\n📋 Bulunan dosyalar:")
for f in pkg.metadata.files:
    print(f"   - {f}")
EOF
```

### 4. Repository'ye Ekle

```bash
# Paketi repository'ye taşı
mv htop-3.3.0.alp my-repo/packages/

# Repository index'i güncelle
python tools/generate_repo_index.py my-repo/packages \
    --name "my-repo" \
    --description "My Custom Repository"
```

### 5. Kur ve Test Et

```bash
# Repository ekle
python alp_cli.py add-repo my-repo "file://$(pwd)/my-repo"

# Index güncelle
python alp_cli.py update

# Paketi kur
python alp_cli.py install htop

# Test et
htop --version
```

## Diğer CMake Örnekleri

### Ninja build sistemi ile

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

### Debug package oluşturma

```bash
cmake .. \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_INSTALL_PREFIX=/usr
make
make install DESTDIR=/tmp/staging-debug

# Debug sembollerle paket oluştur
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

## Önemli Noktalar

1. **Her zaman DESTDIR kullan** - Sisteme direkt kurulum yapma!
2. **PREFIX /usr olmalı** - Paket kurulunca doğru yere gitmesi için
3. **ALP otomatik tarar** - Dosya listesi manuel gerekmiyor
4. **Bağımlılıkları ekle** - CMake'in bulduğu kütüphaneleri dependencies'e yaz

## Sorun Giderme

### DESTDIR çalışmıyor?

Bazı eski CMake projeleri DESTDIR desteklemeyebilir. Çözüm:

```bash
# Install prefix'i staging olarak ayarla
cmake .. -DCMAKE_INSTALL_PREFIX=/tmp/staging/usr
make install

# Paket oluştururken path'i düzelt
pkg = Package.create_package(
    name='myapp',
    version='1.0.0',
    source_dir='/tmp/staging',  # usr/ içerir
    ...
)
```

### Dosyalar bulunamadı?

```bash
# Staging directory'yi kontrol et
find /tmp/staging -type f

# Boşsa, make install loglarını incele
make install VERBOSE=1 DESTDIR=/tmp/staging
```

## Sonuç

CMake → DESTDIR → ALP paketleme akışı ile:
- ✅ Binlerce dosya otomatik bulunur
- ✅ Manuel dosya listesi gerekmez
- ✅ Sistem temiz kalır
- ✅ Profesyonel paketler oluşturursunuz
