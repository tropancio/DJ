"""
DJ - Librería de Documentos Tributarios
========================================

Una librería Python para el manejo integral de documentos tributarios chilenos.

Módulos principales:
- storage: Almacenamiento de datos (DataGenerar, DataDeclaracion, DataSii)
- validator: Validación de documentos tributarios
- generator: Generación de documentos XML
- data: Datos estandarizados y códigos SII
"""

__version__ = "1.0.0"
__author__ = "Maximiliano Alarcon"
__email__ = ""

from .storage import DataGenerar, DataDeclaracion, DataSii
from .validator import DJValidator
from .generator import DJGenerator
from .data import Standards, SiiCodes

class DJ:
    """
    Clase principal de la librería DJ para manejo de documentos tributarios.
    
    Proporciona una interfaz unificada para acceder a todas las funcionalidades
    de almacenamiento, validación y generación de documentos.
    """
    
    def __init__(self):
        """Inicializa la instancia principal de DJ."""
        self.version = __version__
        self.storage = {
            'generar': DataGenerar(),
            'declaracion': DataDeclaracion(),
            'sii': DataSii()
        }
        self.validator = DJValidator()
        self.generator = DJGenerator()
        self.standards = Standards()
        self.sii_codes = SiiCodes()
    
    def get_version(self):
        """Retorna la versión actual de la librería."""
        return self.version
    
    def info(self):
        """Muestra información sobre la librería."""
        print(f"DJ v{self.version} - Librería de Documentos Tributarios")
        print("Módulos disponibles:")
        print("- storage: Almacenamiento de datos")
        print("- validator: Validación de documentos")
        print("- generator: Generación de XML")
        print("- data: Datos estandarizados")

# Exportar las clases principales
__all__ = [
    'DJ',
    'DataGenerar',
    'DataDeclaracion', 
    'DataSii',
    'DJValidator',
    'DJGenerator',
    'Standards',
    'SiiCodes'
]
