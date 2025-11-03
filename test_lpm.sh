#!/bin/bash

echo "🧪 LPM Test Scripti"
echo "===================="
echo ""

echo "📋 1. LPM Yardım Menüsü"
python lpm_cli.py --help
echo ""

echo "📚 2. Repository Ekle (Demo Repo)"
python lpm_cli.py add-repo demo-repo "file://$(pwd)/demo_repo"
echo ""

echo "📦 3. Repository'leri Listele"
python lpm_cli.py list-repos
echo ""

echo "🔄 4. Repository İndekslerini Güncelle"
python lpm_cli.py update
echo ""

echo "🔍 5. Paket Ara (hello)"
python lpm_cli.py search hello
echo ""

echo "📋 6. Mevcut Paketleri Listele"
python lpm_cli.py list --all
echo ""

echo "📦 7. Kurulu Paketleri Listele"
python lpm_cli.py list
echo ""

echo "✅ Test tamamlandı!"
