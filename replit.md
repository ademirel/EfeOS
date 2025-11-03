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
- MVP geliştirme aşamasında
- CLI aracı öncelikli (GUI sonraki aşamada)

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

## Son Değişiklikler
- 2025-11-03: Proje başlatıldı, temel yapı oluşturuldu
