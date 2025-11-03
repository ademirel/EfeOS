"""
ALP - Advanced Linux Packager
Ana CLI arayüzü
"""

import click
import os
import sys
from typing import Optional

from .database import PackageDatabase
from .repository import Repository
from .resolver import DependencyResolver
from .downloader import Downloader
from .transaction import TransactionLog, Transaction, TransactionType, TransactionStatus
from .package import Package


class ALPContext:
    """ALP context sınıfı"""
    
    def __init__(self):
        db_path = os.getenv('ALP_DB_PATH', './alp_data/packages.db')
        cache_dir = os.getenv('ALP_CACHE_DIR', './alp_data/cache')
        log_dir = os.getenv('ALP_LOG_DIR', './alp_data/logs')
        
        self.database = PackageDatabase(db_path)
        self.repository = Repository(self.database, cache_dir)
        self.resolver = DependencyResolver(self.database, self.repository)
        self.downloader = Downloader(cache_dir)
        self.transaction_log = TransactionLog(log_dir)


pass_context = click.make_pass_decorator(ALPContext, ensure=True)


@click.group()
@click.version_option(version='0.1.0')
@click.pass_context
def cli(ctx):
    """ALP - Advanced Linux Packager"""
    ctx.obj = ALPContext()


@cli.command()
@click.argument('packages', nargs=-1, required=True)
@click.option('--yes', '-y', is_flag=True, help='Onay sorma')
@click.option('--no-deps', is_flag=True, help='Bağımlılıkları yükleme')
@pass_context
def install(ctx: ALPContext, packages, yes, no_deps):
    """Paket kur"""
    click.echo(f"📦 {len(packages)} paket kurulacak...")
    
    transaction = Transaction(TransactionType.INSTALL, list(packages))
    transaction.set_status(TransactionStatus.IN_PROGRESS)
    ctx.transaction_log.save_transaction(transaction)
    
    try:
        if not no_deps:
            click.echo("🔍 Bağımlılıklar çözümleniyor...")
            result = ctx.resolver.resolve(list(packages))
            
            if result['missing']:
                click.echo(f"❌ Eksik paketler: {', '.join(result['missing'])}")
                transaction.set_status(TransactionStatus.FAILED, "Eksik bağımlılıklar")
                ctx.transaction_log.save_transaction(transaction)
                return
            
            if result['conflicts']:
                click.echo(f"⚠️  Çakışan paketler: {', '.join(result['conflicts'])}")
                transaction.set_status(TransactionStatus.FAILED, "Çakışan paketler")
                ctx.transaction_log.save_transaction(transaction)
                return
            
            to_install = result['install']
        else:
            to_install = []
            for pkg_name in packages:
                metadata = ctx.repository.get_package_metadata(pkg_name)
                if metadata:
                    to_install.append(metadata)
        
        if not to_install:
            click.echo("✅ Tüm paketler zaten kurulu")
            transaction.set_status(TransactionStatus.COMPLETED)
            ctx.transaction_log.save_transaction(transaction)
            return
        
        click.echo(f"\nKurulacak paketler ({len(to_install)}):")
        total_size = 0
        for pkg in to_install:
            size_mb = pkg.get('size', 0) / (1024 * 1024)
            total_size += pkg.get('size', 0)
            click.echo(f"  - {pkg['name']}-{pkg['version']} ({size_mb:.2f} MB)")
        
        click.echo(f"\nToplam indirme: {total_size / (1024 * 1024):.2f} MB")
        
        if not yes:
            if not click.confirm('Devam edilsin mi?'):
                click.echo("❌ İptal edildi")
                transaction.set_status(TransactionStatus.FAILED, "Kullanıcı iptal etti")
                ctx.transaction_log.save_transaction(transaction)
                return
        
        newly_installed = []
        previously_installed_snapshots = {}
        downloaded_files = []
        
        for pkg in to_install:
            pkg_name = pkg['name']
            
            if ctx.database.is_installed(pkg_name):
                snapshot = ctx.database.get_package(pkg_name)
                if snapshot:
                    previously_installed_snapshots[pkg_name] = snapshot
        
        for pkg in to_install:
            pkg_name = pkg['name']
            pkg_version = pkg['version']
            dest_path = os.path.join(ctx.downloader.cache_dir, f"{pkg_name}-{pkg_version}.lpkg")
            
            try:
                click.echo(f"\n📥 {pkg_name}-{pkg_version} indiriliyor...")
                
                pkg_url = ctx.repository.get_package_url(pkg_name, pkg_version)
                if not pkg_url:
                    raise ValueError(f"URL bulunamadı: {pkg_name}")
                
                def progress_callback(percent, downloaded, total):
                    click.echo(f"\r  İlerleme: {percent:.1f}% ({downloaded}/{total} bytes)", nl=False)
                
                success = ctx.downloader.download(pkg_url, dest_path, progress_callback)
                click.echo()
                
                if not success:
                    raise RuntimeError(f"İndirme başarısız: {pkg_name}")
                
                downloaded_files.append(dest_path)
                click.echo(f"✓ İndirme tamamlandı")
                
                if pkg.get('checksum'):
                    click.echo(f"🔐 Checksum doğrulanıyor...")
                    if not ctx.downloader.verify_checksum(dest_path, pkg['checksum']):
                        raise ValueError(f"Checksum hatası: {pkg_name}")
                    click.echo(f"✓ Checksum doğrulandı")
                
                click.echo(f"📦 Kuruluyor...")
                ctx.database.add_package(pkg)
                
                if pkg_name not in previously_installed_snapshots:
                    newly_installed.append(pkg_name)
                
                transaction.add_action('install', {'package': pkg_name, 'version': pkg_version})
                
                click.echo(f"✅ {pkg_name}-{pkg_version} kuruldu")
            
            except Exception as pkg_error:
                click.echo(f"\n❌ {pkg_name} kurulumu başarısız: {pkg_error}")
                click.echo(f"🔄 Rollback yapılıyor...")
                
                for new_pkg in newly_installed:
                    try:
                        ctx.database.remove_package(new_pkg)
                        click.echo(f"  ↩️  {new_pkg} kaldırıldı")
                    except Exception as rollback_error:
                        click.echo(f"  ⚠️  {new_pkg} rollback hatası: {rollback_error}")
                
                for upgraded_pkg, snapshot in previously_installed_snapshots.items():
                    try:
                        ctx.database.add_package(snapshot)
                        click.echo(f"  ↩️  {upgraded_pkg} eski versiyona döndürüldü")
                    except Exception as restore_error:
                        click.echo(f"  ⚠️  {upgraded_pkg} restore hatası: {restore_error}")
                
                for file_path in downloaded_files:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception:
                        pass
                
                transaction.set_status(TransactionStatus.FAILED, str(pkg_error))
                ctx.transaction_log.save_transaction(transaction)
                raise
        
        transaction.set_status(TransactionStatus.COMPLETED)
        ctx.transaction_log.save_transaction(transaction)
        click.echo("\n✅ Kurulum tamamlandı!")
    
    except Exception as e:
        click.echo(f"\n❌ Hata: {e}")
        transaction.set_status(TransactionStatus.FAILED, str(e))
        ctx.transaction_log.save_transaction(transaction)


@cli.command()
@click.argument('packages', nargs=-1, required=True)
@click.option('--yes', '-y', is_flag=True, help='Onay sorma')
@pass_context
def remove(ctx: ALPContext, packages, yes):
    """Paket kaldır"""
    click.echo(f"🗑️  {len(packages)} paket kaldırılacak...")
    
    transaction = Transaction(TransactionType.REMOVE, list(packages))
    transaction.set_status(TransactionStatus.IN_PROGRESS)
    ctx.transaction_log.save_transaction(transaction)
    
    try:
        for pkg_name in packages:
            if not ctx.database.is_installed(pkg_name):
                click.echo(f"⚠️  {pkg_name} kurulu değil")
                continue
            
            can_remove, reverse_deps = ctx.resolver.can_remove(pkg_name)
            
            if not can_remove:
                click.echo(f"❌ {pkg_name} kaldırılamaz. Bağımlı paketler:")
                for dep in reverse_deps:
                    click.echo(f"  - {dep}")
                continue
            
            if not yes:
                if not click.confirm(f'{pkg_name} kaldırılsın mı?'):
                    click.echo("❌ İptal edildi")
                    continue
            
            click.echo(f"🗑️  {pkg_name} kaldırılıyor...")
            ctx.database.remove_package(pkg_name)
            transaction.add_action('remove', {'package': pkg_name})
            
            click.echo(f"✅ {pkg_name} kaldırıldı")
        
        transaction.set_status(TransactionStatus.COMPLETED)
        ctx.transaction_log.save_transaction(transaction)
        click.echo("\n✅ Kaldırma tamamlandı!")
    
    except Exception as e:
        click.echo(f"\n❌ Hata: {e}")
        transaction.set_status(TransactionStatus.FAILED, str(e))
        ctx.transaction_log.save_transaction(transaction)


@cli.command()
@click.argument('query', required=True)
@pass_context
def search(ctx: ALPContext, query):
    """Paket ara"""
    click.echo(f"🔍 '{query}' aranıyor...")
    
    results = ctx.repository.search_package(query)
    
    if not results:
        click.echo("❌ Sonuç bulunamadı")
        return
    
    click.echo(f"\n{len(results)} paket bulundu:\n")
    
    for pkg in results:
        installed = "✓" if ctx.database.is_installed(pkg['name']) else " "
        click.echo(f"[{installed}] {pkg['name']}-{pkg['version']}")
        click.echo(f"    {pkg.get('description', 'Açıklama yok')}")
        click.echo(f"    Repository: {pkg.get('repository', 'unknown')}")
        click.echo()


@cli.command()
@click.option('--all', '-a', is_flag=True, help='Tüm mevcut paketleri göster')
@pass_context
def list(ctx: ALPContext, all):
    """Kurulu paketleri listele"""
    if all:
        click.echo("📦 Mevcut paketler:\n")
        packages = ctx.repository.list_available_packages()
    else:
        click.echo("📦 Kurulu paketler:\n")
        packages = ctx.database.list_packages()
    
    if not packages:
        click.echo("Paket bulunamadı")
        return
    
    for pkg in packages:
        size_mb = pkg.get('size', 0) / (1024 * 1024)
        click.echo(f"{pkg['name']}-{pkg['version']} ({size_mb:.2f} MB)")
        if pkg.get('description'):
            click.echo(f"  {pkg['description']}")


@cli.command()
@pass_context
def update(ctx: ALPContext):
    """Repository indekslerini güncelle"""
    click.echo("🔄 Repository indeksleri güncelleniyor...")
    
    results = ctx.repository.update_all_indexes()
    
    for repo_name, success in results.items():
        if success:
            click.echo(f"✅ {repo_name}")
        else:
            click.echo(f"❌ {repo_name}")
    
    click.echo("\n✅ Güncelleme tamamlandı!")


@cli.command()
@click.option('--limit', '-l', default=10, help='Gösterilecek kayıt sayısı')
@pass_context
def history(ctx: ALPContext, limit):
    """İşlem geçmişini göster"""
    click.echo("📜 İşlem geçmişi:\n")
    
    transactions = ctx.transaction_log.load_transactions(limit=limit)
    
    if not transactions:
        click.echo("Kayıt bulunamadı")
        return
    
    for trans in reversed(transactions):
        status_icon = {
            'completed': '✅',
            'failed': '❌',
            'in_progress': '⏳',
            'pending': '⏸️',
            'rolled_back': '↩️'
        }.get(trans.status.value, '?')
        
        click.echo(f"{status_icon} [{trans.timestamp}] {trans.type.value}")
        click.echo(f"   Paketler: {', '.join(trans.packages)}")
        if trans.error:
            click.echo(f"   Hata: {trans.error}")
        click.echo()


@cli.command()
@click.argument('name', required=True)
@click.argument('url', required=True)
@click.option('--priority', '-p', default=100, help='Repository önceliği')
@pass_context
def add_repo(ctx: ALPContext, name, url, priority):
    """Repository ekle"""
    click.echo(f"➕ Repository ekleniyor: {name}")
    
    ctx.database.add_repository(name, url, priority)
    
    click.echo(f"✅ {name} eklendi")
    click.echo(f"🔄 İndeks güncelleniyor...")
    
    if ctx.repository.update_index(url):
        click.echo(f"✅ İndeks güncellendi")
    else:
        click.echo(f"❌ İndeks güncellenemedi")


@cli.command()
@pass_context
def list_repos(ctx: ALPContext):
    """Repository'leri listele"""
    click.echo("📚 Repository'ler:\n")
    
    repos = ctx.database.list_repositories()
    
    if not repos:
        click.echo("Repository bulunamadı")
        return
    
    for repo in repos:
        click.echo(f"• {repo['name']}")
        click.echo(f"  URL: {repo['url']}")
        click.echo(f"  Öncelik: {repo['priority']}")
        click.echo()


@cli.command()
@pass_context
def clean(ctx: ALPContext):
    """Cache temizle"""
    click.echo("🧹 Cache temizleniyor...")
    
    count = ctx.downloader.clean_cache()
    
    click.echo(f"✅ {count} dosya silindi")


if __name__ == '__main__':
    cli()
