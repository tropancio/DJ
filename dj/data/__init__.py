"""
Módulo de datos estandarizados para documentos tributarios.

Contiene códigos, tablas y estándares del SII que son consultados
por los otros módulos de la librería.
"""

from .standards import Standards
from .sii_codes import SiiCodes

__all__ = ['Standards', 'SiiCodes']
