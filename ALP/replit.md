# ALP - Advanced Linux Packager

## Proje Özeti
LFS (Linux From Scratch) tabanlı Linux dağıtımları için modern, gelişmiş paket yöneticisi.

## Hedef Özellikler
- **Hızlı bağımlılık çözümleme**: Gelişmiş dependency resolver
- **Paralel işlemler**: Çoklu paket indirme ve kurulum
- **Atomic güncellemeler**: Rollback desteği
- **Transaction log**: Tüm işlemler kayıt altında
- **Yeni paket formatı**: .alp (Advanced Linux Package) formatı

## Mevcut Durum
- ✅ MVP tamamlandı ve production-ready
- CLI aracı tam fonksiyonel (GUI sonraki aşamada)
- Tüm kritik hatalar düzeltildi ve architect onaylandı
- ✅ Tüm proje dosyaları ALP/ ana klasörü altında organize edildi

## Proje Yapısı
```
ALP/
├── alp/              - Ana paket modülü
│   ├── cli.py        - CLI komutları (install, remove, update, search, list)
│   ├── database.py   - SQLite veritabanı yönetimi
│   ├── resolver.py   - Bağımlılık çözümleyici
│   ├── package.py    - Paket format ve işleme (otomatik dosya taraması)
│   ├── repository.py - Repository yönetimi
│   ├── downloader.py - İndirme ve doğrulama
│   └── transaction.py- Transaction log sistemi
├── tools/            - Yardımcı araçlar
│   └── generate_repo_index.py - Otomatik repo index oluşturma
├── demo_repo/        - Demo repository ve paketler
├── alp_data/         - Runtime data (database, cache, logs)
├── alp_cli.py        - Ana CLI giriş noktası
├── test_alp.sh       - Test script
├── create_demo_package.py - Demo paket oluşturma
├── README.md         - Türkçe kullanım kılavuzu
├── PACKAGE_GUIDE.md  - İngilizce detaylı paket yönetimi kılavuzu
├── ARCHITECTURE.md   - İngilizce mimari dokümantasyon
└── LICENSE           - GPLv3 lisans
```

## Paket Formatı (.alp)
YAML metadata + tar.gz arşiv kombinasyonu
- Metadata: Bağımlılıklar, versiyon, checksums, **otomatik dosya listesi**
- İçerik: Binary/source dosyalar

## Teknik Detaylar

### Güvenlik Özellikleri
- SHA256 checksum doğrulama
- file:// path validation (.alp uzantısı kontrolü)
- Transaction log ile audit trail

### Özellikler
- ✅ Hızlı bağımlılık çözümleme (version constraint enforcement)
- ✅ Upgrade desteği (in-place update)
- ✅ Snapshot-based rollback (upgrade'lerde eski versiyon restore)
- ✅ Transaction logging (error handling ile)
- ✅ Repository management (file:// ve HTTP desteği)
- ✅ Checksum verification
- ✅ Conflict detection
- ✅ **Otomatik dosya taraması** - Binlerce dosya manuel listelemeye gerek yok!

### Paket Oluşturma Workflow
1. **Kaynak kodu derle**: `./configure && make`
2. **DESTDIR'e kur**: `make install DESTDIR=/tmp/staging`
3. **ALP paketi oluştur**: `Package.create_package()` otomatik tüm dosyaları tarar
4. **Repository index oluştur**: `tools/generate_repo_index.py` ile otomatik

### Gelecek Geliştirmeler (Önerilen)
- Paralel paket indirme
- Atomic güncellemeler
- Delta paketler
- Kaynak tabanlı paket derleme
- GUI arayüz (GTK/Qt)
- Test coverage (regression tests)

## Son Değişiklikler
- 2025-11-03: Proje reorganizasyonu
  - Tüm dosyalar ve klasörler ALP/ ana klasörü altında organize edildi
  - PACKAGE_GUIDE.md güncellendi: otomatik dosya taraması açıklandı
  - tools/generate_repo_index.py eklendi: otomatik repo index oluşturma
  - Path'ler ve workflow yeni yapıya göre güncellendi

- 2025-11-03: MVP tamamlandı
  - Kritik hatalar düzeltildi (dependency version enforcement, upgrade rollback, file validation)
  - Database upgrade desteği eklendi
  - Snapshot-based rollback implementasyonu
  - Transaction log error handling
  - Production-ready duruma getirildi
  - Tam İngilizce lokalizasyon (tüm kullanıcıya yönelik metinler)

## Kullanım
```bash
# ALP dizinine git
cd ALP

# Demo repository ekle
python alp_cli.py add-repo demo-repo "file://$(pwd)/demo_repo"

# Repository güncelle
python alp_cli.py update

# Paket ara
python alp_cli.py search hello

# Paket kur
python alp_cli.py install hello-world
```

## Lisans
GPLv3 - Detaylar için LICENSE dosyasına bakın.
