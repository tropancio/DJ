"""
Sistema de Declaraciones Juradas del SII (Chile)

Este paquete proporciona herramientas para generar, validar y almacenar
Declaraciones Juradas según las especificaciones del SII.

Módulos principales:
- access_schema: Conexión y consultas a Access
- dispatcher: Orquestador principal del sistema
- validation: Validación de datos
- generation: Generación de archivos SII
- storage: Almacenamiento en Access
- templates: Generación de plantillas Excel
- procedures: Procedimientos especiales por DJ
"""

__version__ = "1.0.0"
__author__ = "Maximiliano Alarcón"
__email__ = "your.email@example.com"

# Importaciones principales para facilitar el uso
from .access_schema import AccessSchema, obtener_metadata
from .dispatcher import DJDispatcher, procesar_dj_desde_excel, procesar_dj_desde_dataframe

__all__ = [
    'AccessSchema',
    'obtener_metadata', 
    'DJDispatcher',
    'procesar_dj_desde_excel',
    'procesar_dj_desde_dataframe'
]
