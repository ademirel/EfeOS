# LPM - Linux Package Manager

Modern, hızlı ve güvenilir paket yöneticisi - LFS tabanlı Linux dağıtımları için.

## Özellikler

### ✨ Temel Özellikler
- **Hızlı Bağımlılık Çözümleme**: Akıllı dependency resolver
- **Yeni Paket Formatı**: `.lpkg` (YAML metadata + tar.gz)
- **Transaction Log**: Tüm işlemler kayıt altında
- **Checksum Doğrulama**: SHA256 ile paket güvenliği
- **Repository Sistemi**: Merkezi paket deposu yönetimi

### 🚀 Gelecek Özellikler
- Atomic güncellemeler ve rollback desteği
- Paralel paket indirme ve kurulum
- Delta paketler (bandwidth optimizasyonu)
- Kaynak tabanlı paket derleme
- GUI arayüz (GTK/Qt)

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

### Temel Komutlar

```bash
# Paket kur
python lpm_cli.py install <paket_adı>

# Paket kaldır
python lpm_cli.py remove <paket_adı>

# Paket ara
python lpm_cli.py search <arama_terimi>

# Kurulu paketleri listele
python lpm_cli.py list

# Tüm mevcut paketleri göster
python lpm_cli.py list --all

# Repository güncelle
python lpm_cli.py update

# İşlem geçmişi
python lpm_cli.py history

# Cache temizle
python lpm_cli.py clean
```

### Repository Yönetimi

```bash
# Repository ekle
python lpm_cli.py add-repo <isim> <url>

# Repository'leri listele
python lpm_cli.py list-repos
```

## Paket Formatı (.lpkg)

LPM, kendi özel paket formatını kullanır:

**Yapı:**
```
paket-name-version.lpkg
├── metadata.yaml    # Paket bilgileri
└── data.tar.gz      # Paket içeriği
```

**metadata.yaml örneği:**
```yaml
name: example-package
version: 1.0.0
description: Örnek paket
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

## Geliştirme

### Proje Yapısı

```
lpm/
├── lpm/
│   ├── __init__.py      # Paket başlatma
│   ├── cli.py           # CLI komutları
│   ├── database.py      # SQLite veritabanı
│   ├── resolver.py      # Bağımlılık çözümleyici
│   ├── package.py       # Paket format işleme
│   ├── repository.py    # Repository yönetimi
│   ├── downloader.py    # İndirme ve doğrulama
│   └── transaction.py   # Transaction log
├── lpm_cli.py           # Ana giriş noktası
├── requirements.txt     # Python bağımlılıkları
└── README.md
```

## Ortam Değişkenleri

```bash
LPM_DB_PATH=/var/lib/lpm/packages.db      # Veritabanı konumu
LPM_CACHE_DIR=/var/cache/lpm              # Cache dizini
LPM_LOG_DIR=/var/log/lpm                  # Log dizini
```

## Lisans

MIT License

## Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.
