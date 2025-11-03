# LPM - Linux Package Manager

## Proje Özeti
LFS (Linux From Scratch) tabanlı Linux dağıtımları için modern, yeni nesil paket yöneticisi.

## Hedef Özellikler
- **Hızlı bağımlılık çözümleme**: Gelişmiş dependency resolver
- **Paralel işlemler**: Çoklu paket indirme ve kurulum
- **Atomic güncellemeler**: Rollback desteği
- **Transaction log**: Tüm işlemler kayıt altında
- **Yeni paket formatı**: .lpkg (LFS Package) formatı

## Mevcut Durum
- ✅ MVP tamamlandı ve production-ready
- CLI aracı tam fonksiyonel (GUI sonraki aşamada)
- Tüm kritik hatalar düzeltildi ve architect onaylandı

## Proje Yapısı
```
lpm/              - Ana paket modülü
├── cli.py        - CLI komutları (install, remove, update, search, list)
├── database.py   - SQLite veritabanı yönetimi
├── resolver.py   - Bağımlılık çözümleyici
├── package.py    - Paket format ve işleme
├── repository.py - Repository yönetimi
├── downloader.py - İndirme ve doğrulama
└── transaction.py- Transaction log sistemi
```

## Paket Formatı (.lpkg)
YAML metadata + tar.gz arşiv kombinasyonu
- Metadata: Bağımlılıklar, versiyon, checksums
- İçerik: Binary/source dosyalar

## Teknik Detaylar

### Güvenlik Özellikleri
- SHA256 checksum doğrulama
- file:// path validation (.lpkg uzantısı kontrolü)
- Transaction log ile audit trail

### Özellikler
- ✅ Hızlı bağımlılık çözümleme (version constraint enforcement)
- ✅ Upgrade desteği (in-place update)
- ✅ Snapshot-based rollback (upgrade'lerde eski versiyon restore)
- ✅ Transaction logging (error handling ile)
- ✅ Repository management (file:// ve HTTP desteği)
- ✅ Checksum verification
- ✅ Conflict detection

### Gelecek Geliştirmeler (Önerilen)
- Paralel paket indirme
- Atomic güncellemeler
- Delta paketler
- Kaynak tabanlı paket derleme
- GUI arayüz (GTK/Qt)
- Test coverage (regression tests)

## Son Değişiklikler
- 2025-11-03: MVP tamamlandı
  - Kritik hatalar düzeltildi (dependency version enforcement, upgrade rollback, file validation)
  - Database upgrade desteği eklendi
  - Snapshot-based rollback implementasyonu
  - Transaction log error handling
  - Production-ready duruma getirildi
