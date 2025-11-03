#!/bin/bash

echo "🧪 ALP Test Scripti"
echo "===================="
echo ""

echo "📋 1. ALP Yardım Menüsü"
python alp_cli.py --help
echo ""

echo "📚 2. Repository Ekle (Demo Repo)"
python alp_cli.py add-repo demo-repo "file://$(pwd)/demo_repo"
echo ""

echo "📦 3. Repository'leri Listele"
python alp_cli.py list-repos
echo ""

echo "🔄 4. Repository İndekslerini Güncelle"
python alp_cli.py update
echo ""

echo "🔍 5. Paket Ara (hello)"
python alp_cli.py search hello
echo ""

echo "📋 6. Mevcut Paketleri Listele"
python alp_cli.py list --all
echo ""

echo "📦 7. Kurulu Paketleri Listele"
python alp_cli.py list
echo ""

echo "✅ Test tamamlandı!"
