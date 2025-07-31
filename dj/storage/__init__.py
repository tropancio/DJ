"""
Módulo de almacenamiento de datos para documentos tributarios.

Contiene las clases para manejar diferentes tipos de datos:
- DataGenerar: Datos para generación de documentos
- DataDeclaracion: Datos de declaraciones
- DataSii: Datos del SII
"""

from .data_generar import DataGenerar
from .data_declaracion import DataDeclaracion
from .data_sii import DataSii

__all__ = ['DataGenerar', 'DataDeclaracion', 'DataSii']
