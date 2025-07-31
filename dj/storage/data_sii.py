"""
DataSii - Módulo para manejo de datos del SII.

Esta clase se encarga de almacenar y gestionar los datos obtenidos
del Servicio de Impuestos Internos (SII).
"""

import json
import datetime
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TipoConsulta(Enum):
    """Tipos de consulta disponibles al SII."""
    RUT_EMPRESA = "rut_empresa"
    ESTADO_DOCUMENTO = "estado_documento" 
    CODIGOS_ACTIVIDAD = "codigos_actividad"
    TIPOS_DOCUMENTO = "tipos_documento"
    TABLA_GENERAL = "tabla_general"


@dataclass
class ConsultaSii:
    """Estructura para almacenar consultas al SII."""
    id_consulta: str
    tipo_consulta: TipoConsulta
    parametros: Dict[str, Any]
    fecha_consulta: datetime.datetime
    respuesta: Dict[str, Any]
    estado: str = "exitosa"
    error: Optional[str] = None


class DataSii:
    """
    Clase para almacenar y gestionar datos del SII.
    
    Funcionalidades:
    - Cache de consultas al SII
    - Validación de RUTs
    - Consulta de códigos y tablas
    - Verificación de estados de documentos
    """
    
    def __init__(self):
        """Inicializa el almacén de datos del SII."""
        self._consultas: List[ConsultaSii] = []
        self._cache: Dict[str, Any] = {}
        self._tablas_sii: Dict[str, Dict[str, Any]] = {}
        self._init_tablas_basicas()
    
    def _init_tablas_basicas(self):
        """Inicializa tablas básicas del SII."""
        # Tipos de documentos tributarios más comunes
        self._tablas_sii['tipos_documento'] = {
            '33': {'nombre': 'Factura Electrónica', 'descripcion': 'Factura electrónica'},
            '34': {'nombre': 'Factura No Afecta', 'descripcion': 'Factura electrónica exenta'},
            '39': {'nombre': 'Boleta Electrónica', 'descripcion': 'Boleta electrónica'},
            '41': {'nombre': 'Boleta No Afecta', 'descripcion': 'Boleta electrónica exenta'},
            '46': {'nombre': 'Factura de Compra', 'descripcion': 'Factura de compra electrónica'},
            '52': {'nombre': 'Guía de Despacho', 'descripcion': 'Guía de despacho electrónica'},
            '56': {'nombre': 'Nota de Débito', 'descripcion': 'Nota de débito electrónica'},
            '61': {'nombre': 'Nota de Crédito', 'descripcion': 'Nota de crédito electrónica'}
        }
        
        # Códigos de actividad económica (muestra)
        self._tablas_sii['actividades_economicas'] = {
            '620200': {'descripcion': 'Consultores en programas de informática'},
            '620100': {'descripcion': 'Programación informática'},
            '631100': {'descripcion': 'Procesamiento de datos'},
            '620900': {'descripcion': 'Otras actividades de informática'}
        }
        
        # Estados de documentos
        self._tablas_sii['estados_documento'] = {
            'ACEPTADO': {'descripcion': 'Documento aceptado por SII'},
            'RECHAZADO': {'descripcion': 'Documento rechazado por SII'},
            'REPARADO': {'descripcion': 'Documento reparado'},
            'PROCESADO': {'descripcion': 'Documento procesado'},
            'PENDIENTE': {'descripcion': 'Documento pendiente de procesamiento'}
        }
    
    def store_consulta(self, tipo_consulta: TipoConsulta, parametros: Dict[str, Any], 
                      respuesta: Dict[str, Any], estado: str = "exitosa", 
                      error: Optional[str] = None) -> str:
        """
        Almacena una consulta realizada al SII.
        
        Args:
            tipo_consulta: Tipo de consulta realizada
            parametros: Parámetros de la consulta
            respuesta: Respuesta obtenida
            estado: Estado de la consulta
            error: Error si lo hubo
            
        Returns:
            str: ID de la consulta almacenada
        """
        # Generar ID único
        timestamp = datetime.datetime.now()
        id_consulta = f"{tipo_consulta.value}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        consulta = ConsultaSii(
            id_consulta=id_consulta,
            tipo_consulta=tipo_consulta,
            parametros=parametros,
            fecha_consulta=timestamp,
            respuesta=respuesta,
            estado=estado,
            error=error
        )
        
        self._consultas.append(consulta)
        
        # Guardar en cache si la consulta fue exitosa
        if estado == "exitosa":
            cache_key = f"{tipo_consulta.value}_{hash(str(parametros))}"
            self._cache[cache_key] = {
                'respuesta': respuesta,
                'fecha': timestamp,
                'parametros': parametros
            }
        
        return id_consulta
    
    def get_from_cache(self, tipo_consulta: TipoConsulta, 
                      parametros: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Recupera una respuesta del cache si existe.
        
        Args:
            tipo_consulta: Tipo de consulta
            parametros: Parámetros de la consulta
            
        Returns:
            Dict con la respuesta cached o None
        """
        cache_key = f"{tipo_consulta.value}_{hash(str(parametros))}"
        return self._cache.get(cache_key)
    
    def validar_rut(self, rut: str) -> Dict[str, Any]:
        """
        Valida un RUT chileno.
        
        Args:
            rut: RUT a validar (con o sin puntos y guión)
            
        Returns:
            Dict con el resultado de la validación
        """
        # Limpiar RUT
        rut_limpio = rut.replace('.', '').replace('-', '').upper()
        
        if len(rut_limpio) < 2:
            return {'valido': False, 'error': 'RUT muy corto'}
        
        # Separar número y dígito verificador
        rut_numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
        
        # Validar que el número sea numérico
        if not rut_numero.isdigit():
            return {'valido': False, 'error': 'RUT contiene caracteres no válidos'}
        
        # Calcular dígito verificador
        suma = 0
        multiplicador = 2
        
        for digito in reversed(rut_numero):
            suma += int(digito) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        resto = suma % 11
        dv_calculado = str(11 - resto) if resto != 0 else '0'
        if dv_calculado == '10':
            dv_calculado = 'K'
        
        es_valido = dv == dv_calculado
        
        return {
            'valido': es_valido,
            'rut_formateado': f"{rut_numero}-{dv}",
            'dv_calculado': dv_calculado,
            'dv_proporcionado': dv
        }
    
    def get_tipo_documento(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un tipo de documento por su código.
        
        Args:
            codigo: Código del tipo de documento
            
        Returns:
            Dict con información del documento o None
        """
        return self._tablas_sii['tipos_documento'].get(codigo)
    
    def get_actividad_economica(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de una actividad económica por su código.
        
        Args:
            codigo: Código de la actividad económica
            
        Returns:
            Dict con información de la actividad o None
        """
        return self._tablas_sii['actividades_economicas'].get(codigo)
    
    def get_estado_documento(self, estado: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un estado de documento.
        
        Args:
            estado: Estado del documento
            
        Returns:
            Dict con información del estado o None
        """
        return self._tablas_sii['estados_documento'].get(estado.upper())
    
    def listar_tipos_documento(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos los tipos de documento disponibles.
        
        Returns:
            Dict con todos los tipos de documento
        """
        return self._tablas_sii['tipos_documento'].copy()
    
    def listar_actividades_economicas(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todas las actividades económicas disponibles.
        
        Returns:
            Dict con todas las actividades económicas
        """
        return self._tablas_sii['actividades_economicas'].copy()
    
    def get_consulta(self, id_consulta: str) -> Optional[ConsultaSii]:
        """
        Recupera una consulta por su ID.
        
        Args:
            id_consulta: ID de la consulta
            
        Returns:
            ConsultaSii o None si no existe
        """
        for consulta in self._consultas:
            if consulta.id_consulta == id_consulta:
                return consulta
        return None
    
    def get_consultas_por_tipo(self, tipo_consulta: TipoConsulta) -> List[ConsultaSii]:
        """
        Recupera todas las consultas de un tipo específico.
        
        Args:
            tipo_consulta: Tipo de consulta a filtrar
            
        Returns:
            Lista de consultas del tipo especificado
        """
        return [c for c in self._consultas if c.tipo_consulta == tipo_consulta]
    
    def clear_cache(self) -> None:
        """Limpia el cache de consultas."""
        self._cache.clear()
    
    def get_estadisticas(self) -> Dict[str, Any]:
        """
        Genera estadísticas de las consultas realizadas.
        
        Returns:
            Dict con estadísticas
        """
        total_consultas = len(self._consultas)
        
        # Contar por tipo
        por_tipo = {}
        for tipo in TipoConsulta:
            count = len(self.get_consultas_por_tipo(tipo))
            por_tipo[tipo.value] = count
        
        # Contar exitosas vs fallidas
        exitosas = len([c for c in self._consultas if c.estado == "exitosa"])
        fallidas = total_consultas - exitosas
        
        return {
            'total_consultas': total_consultas,
            'por_tipo': por_tipo,
            'exitosas': exitosas,
            'fallidas': fallidas,
            'cache_entries': len(self._cache)
        }
    
    def export_json(self, filepath: str) -> None:
        """
        Exporta todas las consultas a un archivo JSON.
        
        Args:
            filepath: Ruta del archivo JSON
        """
        data = []
        for consulta in self._consultas:
            consulta_dict = {
                'id_consulta': consulta.id_consulta,
                'tipo_consulta': consulta.tipo_consulta.value,
                'parametros': consulta.parametros,
                'fecha_consulta': consulta.fecha_consulta.isoformat(),
                'respuesta': consulta.respuesta,
                'estado': consulta.estado,
                'error': consulta.error
            }
            data.append(consulta_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def count(self) -> int:
        """Retorna la cantidad total de consultas almacenadas."""
        return len(self._consultas)
    
    def clear(self) -> None:
        """Limpia todas las consultas y el cache."""
        self._consultas.clear()
        self._cache.clear()
