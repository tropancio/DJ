"""
DataDeclaracion - Módulo para manejo de datos de declaraciones tributarias.

Esta clase se encarga de almacenar y gestionar los datos de declaraciones
enviadas al SII.
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EstadoDeclaracion(Enum):
    """Estados posibles de una declaración."""
    BORRADOR = "borrador"
    ENVIADA = "enviada"
    ACEPTADA = "aceptada"
    RECHAZADA = "rechazada"
    CORREGIDA = "corregida"


@dataclass
class Declaracion:
    """Estructura de datos para una declaración tributaria."""
    folio: str
    periodo: str
    tipo_declaracion: str
    rut_declarante: str
    fecha_declaracion: datetime.date
    monto_total: float
    datos_declaracion: Dict[str, Any]
    estado: EstadoDeclaracion = EstadoDeclaracion.BORRADOR
    fecha_envio: Optional[datetime.date] = None
    respuesta_sii: Optional[Dict[str, Any]] = None


class DataDeclaracion:
    """
    Clase para almacenar y gestionar datos de declaraciones tributarias.
    
    Funcionalidades:
    - Almacenar declaraciones tributarias
    - Gestionar estados de declaraciones
    - Consultar declaraciones por período
    - Generar reportes de declaraciones
    """
    
    def __init__(self):
        """Inicializa el almacén de declaraciones."""
        self._declaraciones: List[Declaracion] = []
        self._indices_folio: Dict[str, int] = {}
        self._indices_periodo: Dict[str, List[int]] = {}
    
    def store(self, declaracion_data: Dict[str, Any]) -> str:
        """
        Almacena una declaración tributaria.
        
        Args:
            declaracion_data: Diccionario con los datos de la declaración
            
        Returns:
            str: Folio de la declaración almacenada
            
        Raises:
            ValueError: Si los datos no tienen la estructura requerida
        """
        # Validar campos requeridos
        required_fields = [
            'folio', 'periodo', 'tipo_declaracion', 
            'rut_declarante', 'fecha_declaracion', 'monto_total'
        ]
        
        for field in required_fields:
            if field not in declaracion_data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Validar que el folio no exista
        if declaracion_data['folio'] in self._indices_folio:
            raise ValueError(f"Folio {declaracion_data['folio']} ya existe")
        
        # Convertir fecha si es string
        fecha_declaracion = declaracion_data['fecha_declaracion']
        if isinstance(fecha_declaracion, str):
            fecha_declaracion = datetime.datetime.strptime(fecha_declaracion, '%Y-%m-%d').date()
        
        # Procesar fecha de envío si existe
        fecha_envio = declaracion_data.get('fecha_envio')
        if fecha_envio and isinstance(fecha_envio, str):
            fecha_envio = datetime.datetime.strptime(fecha_envio, '%Y-%m-%d').date()
        
        # Procesar estado
        estado_str = declaracion_data.get('estado', 'borrador')
        estado = EstadoDeclaracion(estado_str)
        
        # Crear declaración
        declaracion = Declaracion(
            folio=declaracion_data['folio'],
            periodo=declaracion_data['periodo'],
            tipo_declaracion=declaracion_data['tipo_declaracion'],
            rut_declarante=declaracion_data['rut_declarante'],
            fecha_declaracion=fecha_declaracion,
            monto_total=float(declaracion_data['monto_total']),
            datos_declaracion=declaracion_data.get('datos_declaracion', {}),
            estado=estado,
            fecha_envio=fecha_envio,
            respuesta_sii=declaracion_data.get('respuesta_sii')
        )
        
        # Almacenar y crear índices
        index = len(self._declaraciones)
        self._declaraciones.append(declaracion)
        self._indices_folio[declaracion.folio] = index
        
        # Índice por período
        periodo = declaracion.periodo
        if periodo not in self._indices_periodo:
            self._indices_periodo[periodo] = []
        self._indices_periodo[periodo].append(index)
        
        return declaracion.folio
    
    def get(self, folio: str) -> Optional[Declaracion]:
        """
        Recupera una declaración por su folio.
        
        Args:
            folio: Folio de la declaración
            
        Returns:
            Declaracion o None si no existe
        """
        if folio in self._indices_folio:
            index = self._indices_folio[folio]
            return self._declaraciones[index]
        return None
    
    def get_by_periodo(self, periodo: str) -> List[Declaracion]:
        """
        Recupera todas las declaraciones de un período específico.
        
        Args:
            periodo: Período a consultar (formato YYYYMM)
            
        Returns:
            Lista de declaraciones del período
        """
        if periodo in self._indices_periodo:
            indices = self._indices_periodo[periodo]
            return [self._declaraciones[i] for i in indices]
        return []
    
    def get_by_rut(self, rut_declarante: str) -> List[Declaracion]:
        """
        Recupera todas las declaraciones de un RUT específico.
        
        Args:
            rut_declarante: RUT del declarante
            
        Returns:
            Lista de declaraciones del RUT
        """
        return [decl for decl in self._declaraciones 
                if decl.rut_declarante == rut_declarante]
    
    def get_by_estado(self, estado: EstadoDeclaracion) -> List[Declaracion]:
        """
        Recupera declaraciones por estado.
        
        Args:
            estado: Estado a filtrar
            
        Returns:
            Lista de declaraciones con el estado especificado
        """
        return [decl for decl in self._declaraciones if decl.estado == estado]
    
    def update_estado(self, folio: str, nuevo_estado: EstadoDeclaracion, 
                     fecha_envio: Optional[datetime.date] = None,
                     respuesta_sii: Optional[Dict[str, Any]] = None) -> bool:
        """
        Actualiza el estado de una declaración.
        
        Args:
            folio: Folio de la declaración
            nuevo_estado: Nuevo estado
            fecha_envio: Fecha de envío (opcional)
            respuesta_sii: Respuesta del SII (opcional)
            
        Returns:
            bool: True if updated successfully
        """
        declaracion = self.get(folio)
        if declaracion:
            declaracion.estado = nuevo_estado
            if fecha_envio:
                declaracion.fecha_envio = fecha_envio
            if respuesta_sii:
                declaracion.respuesta_sii = respuesta_sii
            return True
        return False
    
    def get_total_por_periodo(self, periodo: str) -> float:
        """
        Calcula el monto total declarado en un período.
        
        Args:
            periodo: Período a consultar
            
        Returns:
            float: Monto total del período
        """
        declaraciones = self.get_by_periodo(periodo)
        return sum(decl.monto_total for decl in declaraciones)
    
    def get_estadisticas(self) -> Dict[str, Any]:
        """
        Genera estadísticas de las declaraciones almacenadas.
        
        Returns:
            Dict con estadísticas
        """
        total_declaraciones = len(self._declaraciones)
        
        # Contar por estado
        estados = {}
        for estado in EstadoDeclaracion:
            count = len(self.get_by_estado(estado))
            estados[estado.value] = count
        
        # Monto total
        monto_total = sum(decl.monto_total for decl in self._declaraciones)
        
        # Períodos únicos
        periodos_unicos = len(self._indices_periodo)
        
        return {
            'total_declaraciones': total_declaraciones,
            'por_estado': estados,
            'monto_total': monto_total,
            'periodos_unicos': periodos_unicos,
            'periodos': list(self._indices_periodo.keys())
        }
    
    def export_periodo_json(self, periodo: str, filepath: str) -> None:
        """
        Exporta las declaraciones de un período a JSON.
        
        Args:
            periodo: Período a exportar
            filepath: Ruta del archivo JSON
        """
        declaraciones = self.get_by_periodo(periodo)
        data = []
        
        for decl in declaraciones:
            decl_dict = {
                'folio': decl.folio,
                'periodo': decl.periodo,
                'tipo_declaracion': decl.tipo_declaracion,
                'rut_declarante': decl.rut_declarante,
                'fecha_declaracion': decl.fecha_declaracion.isoformat(),
                'monto_total': decl.monto_total,
                'datos_declaracion': decl.datos_declaracion,
                'estado': decl.estado.value,
                'fecha_envio': decl.fecha_envio.isoformat() if decl.fecha_envio else None,
                'respuesta_sii': decl.respuesta_sii
            }
            data.append(decl_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def count(self) -> int:
        """Retorna la cantidad total de declaraciones almacenadas."""
        return len(self._declaraciones)
    
    def clear(self) -> None:
        """Limpia todas las declaraciones almacenadas."""
        self._declaraciones.clear()
        self._indices_folio.clear()
        self._indices_periodo.clear()
