"""
Standards - Módulo de estándares y configuraciones.

Contiene configuraciones estándar, formatos y reglas generales
utilizadas en los documentos tributarios.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import re


class TipoMoneda(Enum):
    """Tipos de moneda soportados."""
    PESO_CHILENO = "CLP"
    DOLAR_AMERICANO = "USD"
    EURO = "EUR"
    UF = "CLF"


class TipoImpuesto(Enum):
    """Tipos de impuesto."""
    IVA = "IVA"
    EXENTO = "EXENTO"
    RETENCION = "RETENCION"


@dataclass
class ConfiguracionImpuesto:
    """Configuración de un impuesto."""
    codigo: str
    nombre: str
    tasa: float
    descripcion: str


class Standards:
    """
    Clase que contiene todos los estándares y configuraciones
    utilizados en los documentos tributarios.
    """
    
    def __init__(self):
        """Inicializa los estándares."""
        self._configuraciones_impuestos = self._init_impuestos()
        self._formatos_validacion = self._init_formatos()
        self._configuraciones_documentos = self._init_configuraciones_documentos()
        self._reglas_negocio = self._init_reglas_negocio()
    
    def _init_impuestos(self) -> Dict[str, ConfiguracionImpuesto]:
        """Inicializa las configuraciones de impuestos."""
        return {
            'IVA': ConfiguracionImpuesto(
                codigo='14',
                nombre='IVA',
                tasa=0.19,
                descripcion='Impuesto al Valor Agregado'
            ),
            'EXENTO': ConfiguracionImpuesto(
                codigo='0',
                nombre='EXENTO',
                tasa=0.0,
                descripcion='Exento de impuestos'
            ),
            'RETENCION': ConfiguracionImpuesto(
                codigo='15',
                nombre='RETENCION',
                tasa=0.105,
                descripcion='Retención de impuestos'
            )
        }
    
    def _init_formatos(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa los formatos de validación."""
        return {
            'rut': {
                'patron': r'^\d{1,8}-[0-9Kk]$',
                'descripcion': 'Formato RUT chileno con guión',
                'ejemplo': '12345678-9'
            },
            'rut_sin_guion': {
                'patron': r'^\d{7,8}[0-9Kk]$',
                'descripcion': 'Formato RUT chileno sin guión',
                'ejemplo': '123456789'
            },
            'email': {
                'patron': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'descripcion': 'Formato email válido',
                'ejemplo': 'usuario@empresa.cl'
            },
            'telefono_chile': {
                'patron': r'^\+?56[2-9]\d{8}$',
                'descripcion': 'Formato teléfono chileno',
                'ejemplo': '+56912345678'
            },
            'codigo_postal': {
                'patron': r'^\d{7}$',
                'descripcion': 'Código postal chileno',
                'ejemplo': '1234567'
            },
            'fecha_iso': {
                'patron': r'^\d{4}-\d{2}-\d{2}$',
                'descripcion': 'Fecha en formato ISO',
                'ejemplo': '2024-12-31'
            },
            'monto': {
                'patron': r'^\d+(\.\d{1,2})?$',
                'descripcion': 'Monto con hasta 2 decimales',
                'ejemplo': '1000.50'
            }
        }
    
    def _init_configuraciones_documentos(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa configuraciones específicas por tipo de documento."""
        return {
            '33': {  # Factura Electrónica
                'nombre': 'Factura Electrónica',
                'permite_iva': True,
                'permite_exento': True,
                'requiere_receptor': True,
                'monto_minimo': 0,
                'monto_maximo': None,
                'campos_obligatorios': [
                    'tipo_documento', 'folio', 'fecha_emision',
                    'rut_emisor', 'rut_receptor', 'monto_total'
                ]
            },
            '34': {  # Factura No Afecta o Exenta
                'nombre': 'Factura No Afecta o Exenta',
                'permite_iva': False,
                'permite_exento': True,
                'requiere_receptor': True,
                'monto_minimo': 0,
                'monto_maximo': None,
                'campos_obligatorios': [
                    'tipo_documento', 'folio', 'fecha_emision',
                    'rut_emisor', 'rut_receptor', 'monto_total'
                ]
            },
            '39': {  # Boleta Electrónica
                'nombre': 'Boleta Electrónica',
                'permite_iva': True,
                'permite_exento': True,
                'requiere_receptor': False,
                'monto_minimo': 0,
                'monto_maximo': 1000000,  # Monto máximo para boletas
                'campos_obligatorios': [
                    'tipo_documento', 'folio', 'fecha_emision',
                    'rut_emisor', 'monto_total'
                ]
            },
            '41': {  # Boleta No Afecta o Exenta
                'nombre': 'Boleta No Afecta o Exenta',
                'permite_iva': False,
                'permite_exento': True,
                'requiere_receptor': False,
                'monto_minimo': 0,
                'monto_maximo': 1000000,
                'campos_obligatorios': [
                    'tipo_documento', 'folio', 'fecha_emision',
                    'rut_emisor', 'monto_total'
                ]
            },
            '52': {  # Guía de Despacho
                'nombre': 'Guía de Despacho Electrónica',
                'permite_iva': False,
                'permite_exento': True,
                'requiere_receptor': True,
                'monto_minimo': 0,
                'monto_maximo': None,
                'campos_obligatorios': [
                    'tipo_documento', 'folio', 'fecha_emision',
                    'rut_emisor', 'rut_receptor', 'direccion_despacho'
                ]
            },
            '56': {  # Nota de Débito
                'nombre': 'Nota de Débito Electrónica',
                'permite_iva': True,
                'permite_exento': True,
                'requiere_receptor': True,
                'monto_minimo': 0,
                'monto_maximo': None,
                'campos_obligatorios': [
                    'tipo_documento', 'folio', 'fecha_emision',
                    'rut_emisor', 'rut_receptor', 'monto_total', 'documento_referencia'
                ]
            },
            '61': {  # Nota de Crédito
                'nombre': 'Nota de Crédito Electrónica',
                'permite_iva': True,
                'permite_exento': True,
                'requiere_receptor': True,
                'monto_minimo': 0,
                'monto_maximo': None,
                'campos_obligatorios': [
                    'tipo_documento', 'folio', 'fecha_emision',
                    'rut_emisor', 'rut_receptor', 'monto_total', 'documento_referencia'
                ]
            }
        }
    
    def _init_reglas_negocio(self) -> Dict[str, Any]:
        """Inicializa las reglas de negocio generales."""
        return {
            'iva_tasa_actual': 0.19,
            'dias_maximos_atraso_emision': 30,
            'monto_maximo_boleta': 1000000,
            'longitud_maxima_razon_social': 100,
            'longitud_maxima_direccion': 60,
            'longitud_maxima_giro': 80,
            'folios_minimo': 1,
            'folios_maximo': 999999999,
            'caracteres_especiales_permitidos': ['-', '.', ' ', '(', ')', '/', '&'],
            'monedas_soportadas': ['CLP', 'USD', 'EUR', 'CLF']
        }
    
    def get_configuracion_impuesto(self, tipo_impuesto: str) -> Optional[ConfiguracionImpuesto]:
        """
        Obtiene la configuración de un tipo de impuesto.
        
        Args:
            tipo_impuesto: Tipo de impuesto ('IVA', 'EXENTO', etc.)
            
        Returns:
            ConfiguracionImpuesto o None si no existe
        """
        return self._configuraciones_impuestos.get(tipo_impuesto.upper())
    
    def get_tasa_iva(self) -> float:
        """Obtiene la tasa actual de IVA."""
        return self._reglas_negocio['iva_tasa_actual']
    
    def calcular_iva(self, monto_neto: float) -> float:
        """
        Calcula el IVA sobre un monto neto.
        
        Args:
            monto_neto: Monto neto sobre el cual calcular IVA
            
        Returns:
            float: Monto del IVA
        """
        return round(monto_neto * self.get_tasa_iva())
    
    def calcular_total(self, monto_neto: float, monto_exento: float = 0) -> float:
        """
        Calcula el total de un documento.
        
        Args:
            monto_neto: Monto neto afecto a IVA
            monto_exento: Monto exento de IVA
            
        Returns:
            float: Monto total
        """
        iva = self.calcular_iva(monto_neto)
        return monto_neto + iva + monto_exento
    
    def get_configuracion_documento(self, tipo_documento: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración de un tipo de documento.
        
        Args:
            tipo_documento: Código del tipo de documento
            
        Returns:
            Dict con configuración o None si no existe
        """
        return self._configuraciones_documentos.get(str(tipo_documento))
    
    def get_campos_obligatorios(self, tipo_documento: str) -> List[str]:
        """
        Obtiene los campos obligatorios para un tipo de documento.
        
        Args:
            tipo_documento: Código del tipo de documento
            
        Returns:
            Lista de campos obligatorios
        """
        config = self.get_configuracion_documento(tipo_documento)
        return config.get('campos_obligatorios', []) if config else []
    
    def documento_permite_iva(self, tipo_documento: str) -> bool:
        """
        Verifica si un tipo de documento permite IVA.
        
        Args:
            tipo_documento: Código del tipo de documento
            
        Returns:
            bool: True si permite IVA
        """
        config = self.get_configuracion_documento(tipo_documento)
        return config.get('permite_iva', False) if config else False
    
    def documento_requiere_receptor(self, tipo_documento: str) -> bool:
        """
        Verifica si un tipo de documento requiere receptor.
        
        Args:
            tipo_documento: Código del tipo de documento
            
        Returns:
            bool: True si requiere receptor
        """
        config = self.get_configuracion_documento(tipo_documento)
        return config.get('requiere_receptor', True) if config else True
    
    def validar_formato(self, valor: str, tipo_formato: str) -> bool:
        """
        Valida un valor contra un formato específico.
        
        Args:
            valor: Valor a validar
            tipo_formato: Tipo de formato ('rut', 'email', etc.)
            
        Returns:
            bool: True si el formato es válido
        """
        formato = self._formatos_validacion.get(tipo_formato)
        if not formato:
            return False
        
        patron = formato['patron']
        return bool(re.match(patron, str(valor)))
    
    def get_formatos_disponibles(self) -> Dict[str, str]:
        """
        Obtiene todos los formatos de validación disponibles.
        
        Returns:
            Dict con nombre del formato y su descripción
        """
        return {
            nombre: config['descripcion'] 
            for nombre, config in self._formatos_validacion.items()
        }
    
    def get_tipos_documento_soportados(self) -> Dict[str, str]:
        """
        Obtiene todos los tipos de documento soportados.
        
        Returns:
            Dict con código y nombre de documento
        """
        return {
            codigo: config['nombre']
            for codigo, config in self._configuraciones_documentos.items()
        }
    
    def validar_monto_documento(self, tipo_documento: str, monto: float) -> Tuple[bool, Optional[str]]:
        """
        Valida si un monto es válido para un tipo de documento.
        
        Args:
            tipo_documento: Código del tipo de documento
            monto: Monto a validar
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        config = self.get_configuracion_documento(tipo_documento)
        if not config:
            return False, f"Tipo de documento no soportado: {tipo_documento}"
        
        monto_minimo = config.get('monto_minimo', 0)
        monto_maximo = config.get('monto_maximo')
        
        if monto < monto_minimo:
            return False, f"Monto inferior al mínimo permitido: {monto_minimo}"
        
        if monto_maximo and monto > monto_maximo:
            return False, f"Monto superior al máximo permitido: {monto_maximo}"
        
        return True, None
    
    def get_regla_negocio(self, nombre_regla: str) -> Any:
        """
        Obtiene el valor de una regla de negocio.
        
        Args:
            nombre_regla: Nombre de la regla
            
        Returns:
            Valor de la regla o None si no existe
        """
        return self._reglas_negocio.get(nombre_regla)
    
    def listar_reglas_negocio(self) -> Dict[str, Any]:
        """
        Lista todas las reglas de negocio disponibles.
        
        Returns:
            Dict con todas las reglas
        """
        return self._reglas_negocio.copy()
    
    def es_moneda_soportada(self, codigo_moneda: str) -> bool:
        """
        Verifica si una moneda está soportada.
        
        Args:
            codigo_moneda: Código de la moneda (CLP, USD, etc.)
            
        Returns:
            bool: True si está soportada
        """
        monedas_soportadas = self.get_regla_negocio('monedas_soportadas')
        return codigo_moneda.upper() in monedas_soportadas if monedas_soportadas else False
