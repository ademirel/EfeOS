#!/bin/bash

echo "🧪 ALP Test Script"
echo "===================="
echo ""

echo "📋 1. ALP Help Menu"
python alp_cli.py --help
echo ""

echo "📚 2. Add Repository (Demo Repo)"
python alp_cli.py add-repo demo-repo "file://$(pwd)/demo_repo"
echo ""

echo "📦 3. List Repositories"
python alp_cli.py list-repos
echo ""

echo "🔄 4. Update Repository Indexes"
python alp_cli.py update
echo ""

echo "🔍 5. Search Package (hello)"
python alp_cli.py search hello
echo ""

echo "📋 6. List Available Packages"
python alp_cli.py list --all
echo ""

echo "📦 7. List Installed Packages"
python alp_cli.py list
echo ""

echo "✅ Test completed!"
