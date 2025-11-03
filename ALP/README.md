# ALP - Advanced Linux Packager

Modern, hızlı ve güvenilir paket yöneticisi - LFS tabanlı Linux dağıtımları için.

## Özellikler

### ✨ Temel Özellikler
- **Hızlı Bağımlılık Çözümleme**: Akıllı dependency resolver
- **Yeni Paket Formatı**: `.alp` (YAML metadata + tar.gz)
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
cd ALP
pip install -r requirements.txt
```

## Kullanım

### Temel Komutlar

**Not**: Tüm komutları `ALP/` dizini içinden çalıştırın:

```bash
cd ALP

# Paket kur
python alp_cli.py install <paket_adı>

# Paket kaldır
python alp_cli.py remove <paket_adı>

# Paket ara
python alp_cli.py search <arama_terimi>

# Kurulu paketleri listele
python alp_cli.py list

# Tüm mevcut paketleri göster
python alp_cli.py list --all

# Repository güncelle
python alp_cli.py update

# İşlem geçmişi
python alp_cli.py history

# Cache temizle
python alp_cli.py clean
```

### Repository Yönetimi

```bash
# Repository ekle
python alp_cli.py add-repo <isim> <url>

# Repository'leri listele
python alp_cli.py list-repos
```

## Paket Formatı (.alp)

ALP, kendi özel paket formatını kullanır:

**Yapı:**
```
paket-name-version.alp
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
ALP/
├── alp/                 # Python modülü
│   ├── __init__.py      # Paket başlatma
│   ├── cli.py           # CLI komutları
│   ├── database.py      # SQLite veritabanı
│   ├── resolver.py      # Bağımlılık çözümleyici
│   ├── package.py       # Paket format işleme
│   ├── repository.py    # Repository yönetimi
│   ├── downloader.py    # İndirme ve doğrulama
│   └── transaction.py   # Transaction log
├── tools/               # Yardımcı araçlar
│   └── generate_repo_index.py
├── demo_repo/           # Demo repository
├── alp_data/            # Runtime data
├── alp_cli.py           # Ana giriş noktası
├── test_alp.sh          # Test script
├── create_demo_package.py
├── requirements.txt     # Python bağımlılıkları
├── README.md
├── PACKAGE_GUIDE.md     # Detaylı paket yönetim kılavuzu
└── ARCHITECTURE.md      # Mimari dökümantasyon
```

## Ortam Değişkenleri

```bash
ALP_DB_PATH=/var/lib/alp/packages.db      # Veritabanı konumu
ALP_CACHE_DIR=/var/cache/alp              # Cache dizini
ALP_LOG_DIR=/var/log/alp                  # Log dizini
```

## Dökümantasyon

- **[PACKAGE_GUIDE.md](PACKAGE_GUIDE.md)**: Paket oluşturma, kurma, güncelleme ve kaldırma için detaylı kılavuz
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Sistem mimarisi ve tasarım kararları

## Lisans

Bu proje GNU General Public License v3.0 (GPLv3) altında lisanslanmıştır.

Daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakın veya https://www.gnu.org/licenses/gpl-3.0.html adresini ziyaret edin.

## Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.
