"""
Bağımlılık çözümleme motoru
Hızlı ve akıllı dependency resolution
"""

from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, deque


class DependencyResolver:
    """Bağımlılık çözümleyici"""
    
    def __init__(self, database, repository):
        self.database = database
        self.repository = repository
        self._cache = {}
    
    def parse_dependency(self, dep_string: str) -> Tuple[str, Optional[str]]:
        """Bağımlılık stringini parse et
        Örnek: 'gcc>=11.0' -> ('gcc', '11.0')
        """
        if '>=' in dep_string:
            parts = dep_string.split('>=')
            return parts[0].strip(), parts[1].strip()
        elif '=' in dep_string:
            parts = dep_string.split('=')
            return parts[0].strip(), parts[1].strip()
        else:
            return dep_string.strip(), None
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """Versiyon karşılaştırma
        Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
        """
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    
    def resolve(self, package_names: List[str]) -> Dict:
        """Ana çözümleme fonksiyonu
        Returns: {
            'install': [paket listesi],
            'conflicts': [çakışma listesi],
            'missing': [eksik bağımlılıklar]
        }
        """
        to_install = []
        conflicts = []
        missing = []
        visited = {}
        requirements = {}
        
        queue = deque(package_names)
        
        while queue:
            pkg_name = queue.popleft()
            
            required_version = requirements.get(pkg_name)
            
            if pkg_name in visited:
                prev_req = visited[pkg_name]
                if required_version and prev_req:
                    if self.compare_versions(required_version, prev_req) > 0:
                        visited[pkg_name] = required_version
                    else:
                        continue
                elif not required_version:
                    continue
                else:
                    visited[pkg_name] = required_version
            else:
                visited[pkg_name] = required_version
            
            pkg_metadata = self.repository.get_package_metadata(pkg_name)
            
            if not pkg_metadata:
                missing.append(pkg_name)
                continue
            
            if required_version:
                if self.compare_versions(pkg_metadata['version'], required_version) < 0:
                    missing.append(f"{pkg_name}>={required_version} (mevcut: {pkg_metadata['version']})")
                    continue
            
            if self.database.is_installed(pkg_name):
                installed_pkg = self.database.get_package(pkg_name)
                if installed_pkg:
                    if required_version:
                        if self.compare_versions(installed_pkg['version'], required_version) >= 0:
                            continue
                    elif self.compare_versions(installed_pkg['version'], pkg_metadata['version']) >= 0:
                        continue
            
            if self._check_conflicts(pkg_metadata, to_install):
                conflicts.append(pkg_name)
                continue
            
            already_in_install = False
            for idx, existing_pkg in enumerate(to_install):
                if existing_pkg['name'] == pkg_name:
                    to_install[idx] = pkg_metadata
                    already_in_install = True
                    break
            
            if not already_in_install:
                to_install.append(pkg_metadata)
            
            for dep in pkg_metadata.get('dependencies', []):
                dep_name, dep_version = self.parse_dependency(dep)
                
                if dep_version:
                    existing_req = requirements.get(dep_name)
                    if existing_req:
                        if self.compare_versions(dep_version, existing_req) > 0:
                            requirements[dep_name] = dep_version
                            if dep_name in visited:
                                queue.append(dep_name)
                    else:
                        requirements[dep_name] = dep_version
                
                should_add = True
                if self.database.is_installed(dep_name):
                    installed_pkg = self.database.get_package(dep_name)
                    
                    if dep_version and installed_pkg:
                        if self.compare_versions(installed_pkg['version'], dep_version) < 0:
                            queue.append(dep_name)
                            should_add = False
                        else:
                            should_add = False
                    else:
                        should_add = False
                
                if should_add:
                    queue.append(dep_name)
        
        return {
            'install': to_install,
            'conflicts': conflicts,
            'missing': missing
        }
    
    def _check_conflicts(self, pkg_metadata: Dict, install_list: List[Dict]) -> bool:
        """Çakışma kontrolü"""
        pkg_conflicts = set(pkg_metadata.get('conflicts', []))
        
        for installed_pkg in install_list:
            if installed_pkg['name'] in pkg_conflicts:
                return True
            
            if pkg_metadata['name'] in set(installed_pkg.get('conflicts', [])):
                return True
        
        for conflict_pkg in pkg_conflicts:
            if self.database.is_installed(conflict_pkg):
                return True
        
        return False
    
    def get_reverse_dependencies(self, package_name: str) -> List[str]:
        """Ters bağımlılıklar - hangi paketler buna bağlı?"""
        reverse_deps = []
        
        all_packages = self.database.list_packages()
        
        for pkg in all_packages:
            pkg_full = self.database.get_package(pkg['name'])
            deps = pkg_full.get('dependencies', [])
            
            for dep in deps:
                dep_name, _ = self.parse_dependency(dep)
                if dep_name == package_name:
                    reverse_deps.append(pkg['name'])
                    break
        
        return reverse_deps
    
    def can_remove(self, package_name: str) -> Tuple[bool, List[str]]:
        """Paket kaldırılabilir mi?"""
        reverse_deps = self.get_reverse_dependencies(package_name)
        
        if reverse_deps:
            return False, reverse_deps
        
        return True, []
