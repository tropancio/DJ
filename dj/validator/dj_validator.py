"""
DJValidator - Módulo de validación de documentos tributarios.

Esta clase se encarga de validar documentos tributarios según
las normativas y estándares del SII.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class TipoValidacion(Enum):
    """Tipos de validación disponibles."""
    ESTRUCTURA = "estructura"
    DATOS_OBLIGATORIOS = "datos_obligatorios"
    FORMATO = "formato"
    NEGOCIO = "negocio"
    XML = "xml"


class NivelError(Enum):
    """Niveles de error en validación."""
    ERROR = "error"
    ADVERTENCIA = "advertencia"
    INFORMACION = "informacion"


@dataclass
class ErrorValidacion:
    """Estructura para errores de validación."""
    tipo: TipoValidacion
    nivel: NivelError
    campo: str
    mensaje: str
    codigo: Optional[str] = None
    valor_actual: Optional[Any] = None
    valor_esperado: Optional[Any] = None


class DJValidator:
    """
    Validador de documentos tributarios para DJ.
    
    Realiza validaciones de:
    - Estructura de datos
    - Campos obligatorios
    - Formatos de datos
    - Reglas de negocio
    - Estructura XML
    """
    
    def __init__(self):
        """Inicializa el validador."""
        self._reglas_negocio = self._init_reglas_negocio()
        self._campos_obligatorios = self._init_campos_obligatorios()
        self._formatos = self._init_formatos()
    
    def _init_reglas_negocio(self) -> Dict[str, Any]:
        """Inicializa las reglas de negocio."""
        return {
            'monto_maximo_boleta': 1000000,  # Monto máximo para boletas
            'tipos_documento_validos': ['33', '34', '39', '41', '46', '52', '56', '61'],
            'iva_rate': 0.19,  # Tasa de IVA
            'fecha_maxima_atraso': 30,  # Días máximos de atraso en documentos
        }
    
    def _init_campos_obligatorios(self) -> Dict[str, List[str]]:
        """Inicializa los campos obligatorios por tipo de documento."""
        return {
            '33': [  # Factura Electrónica
                'tipo_documento', 'folio', 'fecha_emision', 'rut_emisor',
                'rut_receptor', 'monto_neto', 'monto_iva', 'monto_total'
            ],
            '39': [  # Boleta Electrónica
                'tipo_documento', 'folio', 'fecha_emision', 'rut_emisor',
                'monto_total'
            ],
            '52': [  # Guía de Despacho
                'tipo_documento', 'folio', 'fecha_emision', 'rut_emisor',
                'rut_receptor', 'direccion_despacho'
            ],
            '61': [  # Nota de Crédito
                'tipo_documento', 'folio', 'fecha_emision', 'rut_emisor',
                'rut_receptor', 'monto_total', 'documento_referencia'
            ]
        }
    
    def _init_formatos(self) -> Dict[str, str]:
        """Inicializa las expresiones regulares para validar formatos."""
        return {
            'rut': r'^\d{1,8}-[0-9Kk]$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'telefono': r'^\+?56\d{8,9}$',
            'fecha_iso': r'^\d{4}-\d{2}-\d{2}$',
            'folio': r'^\d{1,10}$',
            'codigo_postal': r'^\d{7}$'
        }
    
    def validate(self, documento: Dict[str, Any]) -> Tuple[bool, List[ErrorValidacion]]:
        """
        Realiza validación completa de un documento.
        
        Args:
            documento: Diccionario con los datos del documento
            
        Returns:
            Tuple[bool, List[ErrorValidacion]]: (es_valido, lista_errores)
        """
        errores = []
        
        # Validaciones en orden de importancia
        errores.extend(self._validar_estructura(documento))
        errores.extend(self._validar_datos_obligatorios(documento))
        errores.extend(self._validar_formatos(documento))
        errores.extend(self._validar_reglas_negocio(documento))
        
        # Determinar si es válido (solo errores, no advertencias)
        errores_criticos = [e for e in errores if e.nivel == NivelError.ERROR]
        es_valido = len(errores_criticos) == 0
        
        return es_valido, errores
    
    def _validar_estructura(self, documento: Dict[str, Any]) -> List[ErrorValidacion]:
        """Valida la estructura básica del documento."""
        errores = []
        
        # Verificar que sea un diccionario
        if not isinstance(documento, dict):
            errores.append(ErrorValidacion(
                tipo=TipoValidacion.ESTRUCTURA,
                nivel=NivelError.ERROR,
                campo="documento",
                mensaje="El documento debe ser un diccionario",
                valor_actual=type(documento).__name__,
                valor_esperado="dict"
            ))
            return errores
        
        # Verificar que no esté vacío
        if not documento:
            errores.append(ErrorValidacion(
                tipo=TipoValidacion.ESTRUCTURA,
                nivel=NivelError.ERROR,
                campo="documento",
                mensaje="El documento no puede estar vacío"
            ))
        
        return errores
    
    def _validar_datos_obligatorios(self, documento: Dict[str, Any]) -> List[ErrorValidacion]:
        """Valida que estén presentes los campos obligatorios."""
        errores = []
        
        tipo_documento = documento.get('tipo_documento')
        if not tipo_documento:
            errores.append(ErrorValidacion(
                tipo=TipoValidacion.DATOS_OBLIGATORIOS,
                nivel=NivelError.ERROR,
                campo="tipo_documento",
                mensaje="Tipo de documento es obligatorio"
            ))
            return errores
        
        # Obtener campos obligatorios para este tipo de documento
        campos_obligatorios = self._campos_obligatorios.get(str(tipo_documento), [])
        
        for campo in campos_obligatorios:
            if campo not in documento or documento[campo] is None:
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.DATOS_OBLIGATORIOS,
                    nivel=NivelError.ERROR,
                    campo=campo,
                    mensaje=f"Campo obligatorio faltante: {campo}",
                    codigo=f"CAMPO_OBLIGATORIO_{campo.upper()}"
                ))
            elif isinstance(documento[campo], str) and not documento[campo].strip():
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.DATOS_OBLIGATORIOS,
                    nivel=NivelError.ERROR,
                    campo=campo,
                    mensaje=f"Campo obligatorio vacío: {campo}",
                    codigo=f"CAMPO_VACIO_{campo.upper()}"
                ))
        
        return errores
    
    def _validar_formatos(self, documento: Dict[str, Any]) -> List[ErrorValidacion]:
        """Valida los formatos de los campos."""
        errores = []
        
        # Validar RUT emisor
        if 'rut_emisor' in documento:
            if not self._validar_formato_rut(documento['rut_emisor']):
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.FORMATO,
                    nivel=NivelError.ERROR,
                    campo="rut_emisor",
                    mensaje="Formato de RUT emisor inválido",
                    codigo="RUT_FORMATO_INVALIDO",
                    valor_actual=documento['rut_emisor']
                ))
        
        # Validar RUT receptor
        if 'rut_receptor' in documento:
            if not self._validar_formato_rut(documento['rut_receptor']):
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.FORMATO,
                    nivel=NivelError.ERROR,
                    campo="rut_receptor",
                    mensaje="Formato de RUT receptor inválido",
                    codigo="RUT_FORMATO_INVALIDO",
                    valor_actual=documento['rut_receptor']
                ))
        
        # Validar fecha de emisión
        if 'fecha_emision' in documento:
            if not self._validar_formato_fecha(documento['fecha_emision']):
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.FORMATO,
                    nivel=NivelError.ERROR,
                    campo="fecha_emision",
                    mensaje="Formato de fecha de emisión inválido",
                    codigo="FECHA_FORMATO_INVALIDO",
                    valor_actual=documento['fecha_emision'],
                    valor_esperado="YYYY-MM-DD"
                ))
        
        # Validar folio
        if 'folio' in documento:
            if not self._validar_formato_folio(documento['folio']):
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.FORMATO,
                    nivel=NivelError.ERROR,
                    campo="folio",
                    mensaje="Formato de folio inválido",
                    codigo="FOLIO_FORMATO_INVALIDO",
                    valor_actual=documento['folio']
                ))
        
        # Validar email si existe
        if 'email_receptor' in documento and documento['email_receptor']:
            if not re.match(self._formatos['email'], documento['email_receptor']):
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.FORMATO,
                    nivel=NivelError.ADVERTENCIA,
                    campo="email_receptor",
                    mensaje="Formato de email inválido",
                    codigo="EMAIL_FORMATO_INVALIDO",
                    valor_actual=documento['email_receptor']
                ))
        
        return errores
    
    def _validar_reglas_negocio(self, documento: Dict[str, Any]) -> List[ErrorValidacion]:
        """Valida las reglas de negocio."""
        errores = []
        
        tipo_documento = documento.get('tipo_documento')
        
        # Validar tipo de documento válido
        if tipo_documento and str(tipo_documento) not in self._reglas_negocio['tipos_documento_validos']:
            errores.append(ErrorValidacion(
                tipo=TipoValidacion.NEGOCIO,
                nivel=NivelError.ERROR,
                campo="tipo_documento",
                mensaje=f"Tipo de documento no válido: {tipo_documento}",
                codigo="TIPO_DOCUMENTO_INVALIDO",
                valor_actual=tipo_documento,
                valor_esperado=self._reglas_negocio['tipos_documento_validos']
            ))
        
        # Validar monto máximo para boletas
        if tipo_documento in ['39', '41'] and 'monto_total' in documento:
            monto_total = documento['monto_total']
            if isinstance(monto_total, (int, float)) and monto_total > self._reglas_negocio['monto_maximo_boleta']:
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.NEGOCIO,
                    nivel=NivelError.ADVERTENCIA,
                    campo="monto_total",
                    mensaje=f"Monto de boleta excede el máximo recomendado",
                    codigo="MONTO_BOLETA_EXCESIVO",
                    valor_actual=monto_total,
                    valor_esperado=self._reglas_negocio['monto_maximo_boleta']
                ))
        
        # Validar cálculo de IVA para facturas
        if tipo_documento == '33' and all(k in documento for k in ['monto_neto', 'monto_iva', 'monto_total']):
            monto_neto = documento['monto_neto']
            monto_iva = documento['monto_iva']
            monto_total = documento['monto_total']
            
            if all(isinstance(x, (int, float)) for x in [monto_neto, monto_iva, monto_total]):
                iva_calculado = round(monto_neto * self._reglas_negocio['iva_rate'])
                total_calculado = monto_neto + iva_calculado
                
                if abs(monto_iva - iva_calculado) > 1:  # Tolerancia de 1 peso
                    errores.append(ErrorValidacion(
                        tipo=TipoValidacion.NEGOCIO,
                        nivel=NivelError.ERROR,
                        campo="monto_iva",
                        mensaje="Cálculo de IVA incorrecto",
                        codigo="IVA_CALCULO_INCORRECTO",
                        valor_actual=monto_iva,
                        valor_esperado=iva_calculado
                    ))
                
                if abs(monto_total - total_calculado) > 1:  # Tolerancia de 1 peso
                    errores.append(ErrorValidacion(
                        tipo=TipoValidacion.NEGOCIO,
                        nivel=NivelError.ERROR,
                        campo="monto_total",
                        mensaje="Cálculo de total incorrecto",
                        codigo="TOTAL_CALCULO_INCORRECTO",
                        valor_actual=monto_total,
                        valor_esperado=total_calculado
                    ))
        
        # Validar fecha de emisión no muy antigua
        if 'fecha_emision' in documento:
            fecha_emision = self._parse_fecha(documento['fecha_emision'])
            if fecha_emision:
                dias_diferencia = (datetime.now().date() - fecha_emision).days
                if dias_diferencia > self._reglas_negocio['fecha_maxima_atraso']:
                    errores.append(ErrorValidacion(
                        tipo=TipoValidacion.NEGOCIO,
                        nivel=NivelError.ADVERTENCIA,
                        campo="fecha_emision",
                        mensaje=f"Fecha de emisión muy antigua ({dias_diferencia} días)",
                        codigo="FECHA_ANTIGUA",
                        valor_actual=fecha_emision,
                        valor_esperado=f"Máximo {self._reglas_negocio['fecha_maxima_atraso']} días"
                    ))
        
        return errores
    
    def _validar_formato_rut(self, rut: str) -> bool:
        """Valida el formato de un RUT."""
        if not isinstance(rut, str):
            return False
        return bool(re.match(self._formatos['rut'], rut))
    
    def _validar_formato_fecha(self, fecha: Any) -> bool:
        """Valida el formato de una fecha."""
        if isinstance(fecha, str):
            return bool(re.match(self._formatos['fecha_iso'], fecha))
        elif isinstance(fecha, date):
            return True
        return False
    
    def _validar_formato_folio(self, folio: Any) -> bool:
        """Valida el formato de un folio."""
        if isinstance(folio, int):
            return folio > 0
        elif isinstance(folio, str):
            return bool(re.match(self._formatos['folio'], folio))
        return False
    
    def _parse_fecha(self, fecha: Any) -> Optional[date]:
        """Convierte una fecha a objeto date."""
        if isinstance(fecha, date):
            return fecha
        elif isinstance(fecha, str):
            try:
                return datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return None
        return None
    
    def validate_xml(self, xml_content: str) -> Tuple[bool, List[ErrorValidacion]]:
        """
        Valida la estructura XML de un documento.
        
        Args:
            xml_content: Contenido XML del documento
            
        Returns:
            Tuple[bool, List[ErrorValidacion]]: (es_valido, lista_errores)
        """
        errores = []
        
        try:
            # Intentar parsear el XML
            root = ET.fromstring(xml_content)
            
            # Validaciones básicas de estructura XML
            if not root.tag:
                errores.append(ErrorValidacion(
                    tipo=TipoValidacion.XML,
                    nivel=NivelError.ERROR,
                    campo="xml_root",
                    mensaje="XML no tiene elemento raíz válido"
                ))
            
        except ET.ParseError as e:
            errores.append(ErrorValidacion(
                tipo=TipoValidacion.XML,
                nivel=NivelError.ERROR,
                campo="xml_structure",
                mensaje=f"Error de parsing XML: {str(e)}",
                codigo="XML_PARSE_ERROR"
            ))
        except Exception as e:
            errores.append(ErrorValidacion(
                tipo=TipoValidacion.XML,
                nivel=NivelError.ERROR,
                campo="xml_general",
                mensaje=f"Error general en validación XML: {str(e)}",
                codigo="XML_GENERAL_ERROR"
            ))
        
        es_valido = len([e for e in errores if e.nivel == NivelError.ERROR]) == 0
        return es_valido, errores
    
    def get_resumen_validacion(self, errores: List[ErrorValidacion]) -> Dict[str, Any]:
        """
        Genera un resumen de los errores de validación.
        
        Args:
            errores: Lista de errores de validación
            
        Returns:
            Dict con resumen de errores
        """
        total_errores = len(errores)
        
        # Contar por nivel
        por_nivel = {
            NivelError.ERROR.value: len([e for e in errores if e.nivel == NivelError.ERROR]),
            NivelError.ADVERTENCIA.value: len([e for e in errores if e.nivel == NivelError.ADVERTENCIA]),
            NivelError.INFORMACION.value: len([e for e in errores if e.nivel == NivelError.INFORMACION])
        }
        
        # Contar por tipo
        por_tipo = {}
        for tipo in TipoValidacion:
            count = len([e for e in errores if e.tipo == tipo])
            por_tipo[tipo.value] = count
        
        # Campos con errores
        campos_con_errores = list(set(e.campo for e in errores))
        
        return {
            'total_errores': total_errores,
            'por_nivel': por_nivel,
            'por_tipo': por_tipo,
            'campos_con_errores': campos_con_errores,
            'es_valido': por_nivel[NivelError.ERROR.value] == 0
        }
