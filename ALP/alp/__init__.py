"""
ALP - Advanced Linux Packager
Modern, fast, and reliable package manager for EfeOS

Copyright (C) 2025 ALP Project Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

__version__ = "0.1.0"
__author__ = "ALP Project Contributors"
__license__ = "GPL-3.0"

from .package import Package
from .database import PackageDatabase
from .resolver import DependencyResolver
from .repository import Repository

__all__ = ['Package', 'PackageDatabase', 'DependencyResolver', 'Repository']
