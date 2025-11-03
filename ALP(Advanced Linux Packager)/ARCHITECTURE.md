# ALP Mimari Dokümantasyonu

## Genel Bakış

ALP, modern paket yönetimi prensipleriyle tasarlanmış modüler bir sistemdir.

## Modül Yapısı

### 1. Package (alp/package.py)
**Sorumluluk**: Paket formatı ve işleme

- `.alp` format tanımı (YAML metadata + tar.gz data)
- Paket oluşturma ve yükleme
- SHA256 checksum hesaplama ve doğrulama
- Paket içeriği extraction

**Önemli Sınıflar**:
- `PackageMetadata`: Paket meta verisi (dataclass)
- `Package`: Paket işleme sınıfı

### 2. Database (alp/database.py)
**Sorumluluk**: Kurulu paket durumu yönetimi

- SQLite tabanlı paket tracking
- Upgrade desteği (UPDATE OR INSERT)
- Dependency ve file listesi saklama
- Repository yönetimi

**Önemli Fonksiyonlar**:
- `add_package()`: Yeni paket ekle veya güncelle
- `get_package()`: Tam metadata ile paket bilgisi (files, dependencies dahil)
- `remove_package()`: Paket ve ilişkili verileri sil

**Tablolar**:
- `packages`: Ana paket bilgileri
- `dependencies`: Paket bağımlılıkları
- `files`: Paket dosya listesi
- `repositories`: Repository bilgileri

### 3. Resolver (alp/resolver.py)
**Sorumluluk**: Bağımlılık çözümleme

- Version constraint tracking
- Bağımlılık grafiği çözümleme
- Conflict detection
- Upgrade requirement detection

**Önemli Algoritmalar**:
- BFS-based dependency resolution
- Version comparison (semantic versioning)
- Re-evaluation mechanism (daha sıkı constraint geldiğinde)

**Çıktı**:
```python
{
    'install': [paket listesi],
    'conflicts': [çakışan paketler],
    'missing': [bulunamayan/uyumsuz paketler]
}
```

### 4. Repository (alp/repository.py)
**Sorumluluk**: Paket deposu yönetimi

- Repository index güncelleme (HTTP ve file://)
- Paket arama
- Metadata sorgulama
- Index caching

**Index Formatı**:
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
**Sorumluluk**: Paket indirme ve doğrulama

- HTTP ve file:// protokol desteği
- Progress callback
- Checksum doğrulama
- Cache yönetimi

**Güvenlik**:
- file:// path validation
- .alp uzantısı kontrolü
- Dosya varlık kontrolü

### 6. Transaction (alp/transaction.py)
**Sorumluluk**: İşlem kayıt sistemi

- Transaction logging (append-only)
- Transaction durumu tracking
- Error handling (corrupted line skip)
- History yönetimi

**Transaction States**:
- PENDING
- IN_PROGRESS
- COMPLETED
- FAILED
- ROLLED_BACK

### 7. CLI (alp/cli.py)
**Sorumluluk**: Kullanıcı arayüzü

- Komut işleme (install, remove, search, vb.)
- Snapshot-based rollback
- Progress display
- Error handling

**Rollback Mekanizması**:
1. Transaction başlangıcında mevcut paketlerin snapshot'ı alınır
2. Her paket kurulurken başarısızlık takip edilir
3. Hata durumunda:
   - Yeni kurulan paketler silinir
   - Upgrade edilen paketler eski versiyonuna döndürülür
   - İndirilen dosyalar temizlenir

## Veri Akışı

### Paket Kurulumu
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

### Hata Durumu Rollback
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

## Tasarım Prensipleri

### 1. Separation of Concerns
Her modül tek bir sorumluluğa sahip ve bağımsız test edilebilir.

### 2. Error Recovery
Tüm kritik işlemlerde rollback mekanizması mevcut.

### 3. Data Integrity
- Checksum doğrulama
- Transaction logging
- Database ACID özellikleri

### 4. Security
- Path validation
- File type checking
- No arbitrary code execution

### 5. Extensibility
- Plugin-ready architecture
- Repository system
- Modular design

## Gelecek Geliştirmeler

### Öncelik 1: Core Improvements
- Paralel paket indirme
- Atomic upgrades (system snapshot)
- Delta paketler

### Öncelik 2: Advanced Features
- Kaynak tabanlı paket derleme
- Package signing (GPG)
- Dependency conflict resolution improvements

### Öncelik 3: UI/UX
- GUI (GTK/Qt)
- TUI (ncurses)
- Web interface

## Test Stratejisi

### Unit Tests (Önerilir)
- Package creation/verification
- Version comparison
- Dependency resolution
- Database operations

### Integration Tests (Önerilir)
- Full install/remove cycle
- Upgrade scenarios
- Rollback functionality
- Conflict detection

### Regression Tests (Kritik)
- Upgrade rollback (snapshot restore)
- Version constraint enforcement
- file:// validation
- Transaction log corruption handling
