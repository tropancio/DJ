"""
DataGenerar - Módulo para manejo de datos de generación de documentos.

Esta clase se encarga de almacenar y gestionar los datos necesarios
para la generación de documentos tributarios.
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class DocumentoGeneracion:
    """Estructura de datos para documento en generación."""
    tipo_documento: str
    rut_emisor: str
    rut_receptor: str
    fecha_emision: datetime.date
    datos: Dict[str, Any]
    estado: str = "pendiente"


class DataGenerar:
    """
    Clase para almacenar y gestionar datos de generación de documentos tributarios.
    
    Funcionalidades:
    - Almacenar datos de documentos por generar
    - Validar estructura de datos
    - Recuperar datos por diferentes criterios
    - Gestionar estado de documentos
    """
    
    def __init__(self):
        """Inicializa el almacén de datos de generación."""
        self._documentos: List[DocumentoGeneracion] = []
        self._indices: Dict[str, int] = {}
    
    def store(self, documento_data: Dict[str, Any]) -> str:
        """
        Almacena datos de un documento para generación.
        
        Args:
            documento_data: Diccionario con los datos del documento
            
        Returns:
            str: ID único del documento almacenado
            
        Raises:
            ValueError: Si los datos no tienen la estructura requerida
        """
        # Validar estructura mínima
        required_fields = ['tipo_documento', 'rut_emisor', 'rut_receptor', 'fecha_emision']
        for field in required_fields:
            if field not in documento_data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Convertir fecha si es string
        fecha_emision = documento_data['fecha_emision']
        if isinstance(fecha_emision, str):
            fecha_emision = datetime.datetime.strptime(fecha_emision, '%Y-%m-%d').date()
        
        # Crear documento
        documento = DocumentoGeneracion(
            tipo_documento=documento_data['tipo_documento'],
            rut_emisor=documento_data['rut_emisor'],
            rut_receptor=documento_data['rut_receptor'],
            fecha_emision=fecha_emision,
            datos=documento_data.get('datos', {}),
            estado=documento_data.get('estado', 'pendiente')
        )
        
        # Generar ID único
        doc_id = f"{documento.rut_emisor}_{documento.tipo_documento}_{len(self._documentos)}"
        
        # Almacenar
        self._documentos.append(documento)
        self._indices[doc_id] = len(self._documentos) - 1
        
        return doc_id
    
    def get(self, doc_id: str) -> Optional[DocumentoGeneracion]:
        """
        Recupera un documento por su ID.
        
        Args:
            doc_id: ID del documento
            
        Returns:
            DocumentoGeneracion o None si no existe
        """
        if doc_id in self._indices:
            index = self._indices[doc_id]
            return self._documentos[index]
        return None
    
    def get_by_rut_emisor(self, rut_emisor: str) -> List[DocumentoGeneracion]:
        """
        Recupera todos los documentos de un emisor específico.
        
        Args:
            rut_emisor: RUT del emisor
            
        Returns:
            Lista de documentos del emisor
        """
        return [doc for doc in self._documentos if doc.rut_emisor == rut_emisor]
    
    def get_by_estado(self, estado: str) -> List[DocumentoGeneracion]:
        """
        Recupera documentos por estado.
        
        Args:
            estado: Estado a filtrar (pendiente, procesado, error, etc.)
            
        Returns:
            Lista de documentos con el estado especificado
        """
        return [doc for doc in self._documentos if doc.estado == estado]
    
    def update_estado(self, doc_id: str, nuevo_estado: str) -> bool:
        """
        Actualiza el estado de un documento.
        
        Args:
            doc_id: ID del documento
            nuevo_estado: Nuevo estado del documento
            
        Returns:
            bool: True si se actualizó correctamente
        """
        documento = self.get(doc_id)
        if documento:
            documento.estado = nuevo_estado
            return True
        return False
    
    def delete(self, doc_id: str) -> bool:
        """
        Elimina un documento del almacén.
        
        Args:
            doc_id: ID del documento a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        if doc_id in self._indices:
            index = self._indices[doc_id]
            del self._documentos[index]
            del self._indices[doc_id]
            
            # Reindexar
            self._indices = {
                id_doc: i for i, id_doc in enumerate(self._indices.keys())
            }
            return True
        return False
    
    def count(self) -> int:
        """Retorna la cantidad total de documentos almacenados."""
        return len(self._documentos)
    
    def export_json(self, filepath: str) -> None:
        """
        Exporta todos los datos a un archivo JSON.
        
        Args:
            filepath: Ruta del archivo JSON
        """
        data = []
        for doc in self._documentos:
            doc_dict = {
                'tipo_documento': doc.tipo_documento,
                'rut_emisor': doc.rut_emisor,
                'rut_receptor': doc.rut_receptor,
                'fecha_emision': doc.fecha_emision.isoformat(),
                'datos': doc.datos,
                'estado': doc.estado
            }
            data.append(doc_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def clear(self) -> None:
        """Limpia todos los datos almacenados."""
        self._documentos.clear()
        self._indices.clear()
