"""
DJGenerator - Módulo de generación de documentos tributarios XML.

Esta clase se encarga de generar documentos tributarios en formato XML
según las especificaciones del SII.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass
import base64
import hashlib


@dataclass
class ConfiguracionGeneracion:
    """Configuración para generación de documentos."""
    incluir_firma: bool = False
    formato_fecha: str = "%Y-%m-%d"
    encoding: str = "UTF-8"
    indent: bool = True


class DJGenerator:
    """
    Generador de documentos tributarios XML para DJ.
    
    Genera XML de documentos tributarios según estándares del SII:
    - Facturas electrónicas
    - Boletas electrónicas
    - Guías de despacho
    - Notas de crédito y débito
    """
    
    def __init__(self, config: Optional[ConfiguracionGeneracion] = None):
        """
        Inicializa el generador.
        
        Args:
            config: Configuración personalizada de generación
        """
        self.config = config or ConfiguracionGeneracion()
        self._templates = self._init_templates()
        self._namespaces = self._init_namespaces()
    
    def _init_templates(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa las plantillas de documentos."""
        return {
            '33': {  # Factura Electrónica
                'nombre': 'Factura Electrónica',
                'elementos_obligatorios': [
                    'RUTEmisor', 'RUTRecep', 'FchEmis', 'MntNeto', 'MntExe', 'MntTotal'
                ]
            },
            '39': {  # Boleta Electrónica
                'nombre': 'Boleta Electrónica',
                'elementos_obligatorios': [
                    'RUTEmisor', 'FchEmis', 'MntTotal'
                ]
            },
            '52': {  # Guía de Despacho
                'nombre': 'Guía de Despacho Electrónica',
                'elementos_obligatorios': [
                    'RUTEmisor', 'RUTRecep', 'FchEmis', 'DirOrigen', 'DirDest'
                ]
            },
            '61': {  # Nota de Crédito
                'nombre': 'Nota de Crédito Electrónica',
                'elementos_obligatorios': [
                    'RUTEmisor', 'RUTRecep', 'FchEmis', 'MntTotal', 'FolioRef'
                ]
            }
        }
    
    def _init_namespaces(self) -> Dict[str, str]:
        """Inicializa los namespaces XML."""
        return {
            'dte': 'http://www.sii.cl/SiiDte',
            'ds': 'http://www.w3.org/2000/09/xmldsig#',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
    
    def generate(self, documento_data: Dict[str, Any]) -> str:
        """
        Genera un documento XML completo.
        
        Args:
            documento_data: Diccionario con los datos del documento
            
        Returns:
            str: XML del documento generado
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar datos básicos
        if not isinstance(documento_data, dict):
            raise ValueError("Los datos del documento deben ser un diccionario")
        
        tipo_documento = documento_data.get('tipo_documento')
        if not tipo_documento:
            raise ValueError("Tipo de documento es obligatorio")
        
        if str(tipo_documento) not in self._templates:
            raise ValueError(f"Tipo de documento no soportado: {tipo_documento}")
        
        # Generar documento según el tipo
        if str(tipo_documento) == '33':
            return self._generate_factura_electronica(documento_data)
        elif str(tipo_documento) == '39':
            return self._generate_boleta_electronica(documento_data)
        elif str(tipo_documento) == '52':
            return self._generate_guia_despacho(documento_data)
        elif str(tipo_documento) == '61':
            return self._generate_nota_credito(documento_data)
        else:
            return self._generate_documento_generico(documento_data)
    
    def _generate_factura_electronica(self, data: Dict[str, Any]) -> str:
        """Genera XML de factura electrónica."""
        # Crear elemento raíz
        dte = ET.Element('DTE', {
            'xmlns': self._namespaces['dte'],
            'version': '1.0'
        })
        
        # Documento
        documento = ET.SubElement(dte, 'Documento', {'ID': 'F' + str(data.get('folio', '1'))})
        
        # Encabezado
        encabezado = ET.SubElement(documento, 'Encabezado')
        
        # ID del documento
        id_doc = ET.SubElement(encabezado, 'IdDoc')
        ET.SubElement(id_doc, 'TipoDTE').text = str(data['tipo_documento'])
        ET.SubElement(id_doc, 'Folio').text = str(data.get('folio', '1'))
        ET.SubElement(id_doc, 'FchEmis').text = self._format_fecha(data.get('fecha_emision'))
        
        # Emisor
        emisor = ET.SubElement(encabezado, 'Emisor')
        ET.SubElement(emisor, 'RUTEmisor').text = data.get('rut_emisor', '')
        ET.SubElement(emisor, 'RznSoc').text = data.get('razon_social_emisor', 'Empresa Emisora')
        ET.SubElement(emisor, 'GiroEmis').text = data.get('giro_emisor', 'Servicios Generales')
        
        # Agregar dirección emisor si existe
        if 'direccion_emisor' in data:
            ET.SubElement(emisor, 'DirOrigen').text = data['direccion_emisor']
        if 'comuna_emisor' in data:
            ET.SubElement(emisor, 'CmnaOrigen').text = data['comuna_emisor']
        if 'ciudad_emisor' in data:
            ET.SubElement(emisor, 'CiudadOrigen').text = data['ciudad_emisor']
        
        # Receptor
        receptor = ET.SubElement(encabezado, 'Receptor')
        ET.SubElement(receptor, 'RUTRecep').text = data.get('rut_receptor', '')
        ET.SubElement(receptor, 'RznSocRecep').text = data.get('razon_social_receptor', 'Cliente')
        ET.SubElement(receptor, 'GiroRecep').text = data.get('giro_receptor', 'Actividades Varias')
        
        # Agregar dirección receptor si existe
        if 'direccion_receptor' in data:
            ET.SubElement(receptor, 'DirRecep').text = data['direccion_receptor']
        if 'comuna_receptor' in data:
            ET.SubElement(receptor, 'CmnaRecep').text = data['comuna_receptor']
        if 'ciudad_receptor' in data:
            ET.SubElement(receptor, 'CiudadRecep').text = data['ciudad_receptor']
        
        # Totales
        totales = ET.SubElement(encabezado, 'Totales')
        if 'monto_neto' in data:
            ET.SubElement(totales, 'MntNeto').text = str(int(data['monto_neto']))
        if 'monto_exento' in data:
            ET.SubElement(totales, 'MntExe').text = str(int(data['monto_exento']))
        if 'monto_iva' in data:
            ET.SubElement(totales, 'IVA').text = str(int(data['monto_iva']))
        if 'monto_total' in data:
            ET.SubElement(totales, 'MntTotal').text = str(int(data['monto_total']))
        
        # Detalles
        if 'detalle' in data and data['detalle']:
            for i, item in enumerate(data['detalle'], 1):
                detalle = ET.SubElement(documento, 'Detalle')
                ET.SubElement(detalle, 'NroLinDet').text = str(i)
                ET.SubElement(detalle, 'NmbItem').text = item.get('nombre', f'Item {i}')
                ET.SubElement(detalle, 'QtyItem').text = str(item.get('cantidad', 1))
                ET.SubElement(detalle, 'PrcItem').text = str(item.get('precio', 0))
                ET.SubElement(detalle, 'MontoItem').text = str(item.get('monto', 0))
        
        return self._xml_to_string(dte)
    
    def _generate_boleta_electronica(self, data: Dict[str, Any]) -> str:
        """Genera XML de boleta electrónica."""
        # Crear elemento raíz
        dte = ET.Element('DTE', {
            'xmlns': self._namespaces['dte'],
            'version': '1.0'
        })
        
        # Documento
        documento = ET.SubElement(dte, 'Documento', {'ID': 'B' + str(data.get('folio', '1'))})
        
        # Encabezado
        encabezado = ET.SubElement(documento, 'Encabezado')
        
        # ID del documento
        id_doc = ET.SubElement(encabezado, 'IdDoc')
        ET.SubElement(id_doc, 'TipoDTE').text = str(data['tipo_documento'])
        ET.SubElement(id_doc, 'Folio').text = str(data.get('folio', '1'))
        ET.SubElement(id_doc, 'FchEmis').text = self._format_fecha(data.get('fecha_emision'))
        
        # Emisor
        emisor = ET.SubElement(encabezado, 'Emisor')
        ET.SubElement(emisor, 'RUTEmisor').text = data.get('rut_emisor', '')
        ET.SubElement(emisor, 'RznSoc').text = data.get('razon_social_emisor', 'Empresa Emisora')
        ET.SubElement(emisor, 'GiroEmis').text = data.get('giro_emisor', 'Servicios Generales')
        
        # Totales
        totales = ET.SubElement(encabezado, 'Totales')
        if 'monto_total' in data:
            ET.SubElement(totales, 'MntTotal').text = str(int(data['monto_total']))
        
        # Para boletas, el receptor es opcional
        if data.get('rut_receptor'):
            receptor = ET.SubElement(encabezado, 'Receptor')
            ET.SubElement(receptor, 'RUTRecep').text = data['rut_receptor']
            if data.get('razon_social_receptor'):
                ET.SubElement(receptor, 'RznSocRecep').text = data['razon_social_receptor']
        
        return self._xml_to_string(dte)
    
    def _generate_guia_despacho(self, data: Dict[str, Any]) -> str:
        """Genera XML de guía de despacho."""
        # Crear elemento raíz
        dte = ET.Element('DTE', {
            'xmlns': self._namespaces['dte'],
            'version': '1.0'
        })
        
        # Documento
        documento = ET.SubElement(dte, 'Documento', {'ID': 'G' + str(data.get('folio', '1'))})
        
        # Encabezado
        encabezado = ET.SubElement(documento, 'Encabezado')
        
        # ID del documento
        id_doc = ET.SubElement(encabezado, 'IdDoc')
        ET.SubElement(id_doc, 'TipoDTE').text = str(data['tipo_documento'])
        ET.SubElement(id_doc, 'Folio').text = str(data.get('folio', '1'))
        ET.SubElement(id_doc, 'FchEmis').text = self._format_fecha(data.get('fecha_emision'))
        
        # Emisor
        emisor = ET.SubElement(encabezado, 'Emisor')
        ET.SubElement(emisor, 'RUTEmisor').text = data.get('rut_emisor', '')
        ET.SubElement(emisor, 'RznSoc').text = data.get('razon_social_emisor', 'Empresa Emisora')
        
        # Receptor
        receptor = ET.SubElement(encabezado, 'Receptor')
        ET.SubElement(receptor, 'RUTRecep').text = data.get('rut_receptor', '')
        ET.SubElement(receptor, 'RznSocRecep').text = data.get('razon_social_receptor', 'Cliente')
        
        # Transporte
        if data.get('direccion_despacho'):
            transporte = ET.SubElement(encabezado, 'Transporte')
            ET.SubElement(transporte, 'DirDest').text = data['direccion_despacho']
            if data.get('comuna_despacho'):
                ET.SubElement(transporte, 'CmnaDest').text = data['comuna_despacho']
            if data.get('ciudad_despacho'):
                ET.SubElement(transporte, 'CiudadDest').text = data['ciudad_despacho']
        
        return self._xml_to_string(dte)
    
    def _generate_nota_credito(self, data: Dict[str, Any]) -> str:
        """Genera XML de nota de crédito."""
        # Crear elemento raíz
        dte = ET.Element('DTE', {
            'xmlns': self._namespaces['dte'],
            'version': '1.0'
        })
        
        # Documento
        documento = ET.SubElement(dte, 'Documento', {'ID': 'NC' + str(data.get('folio', '1'))})
        
        # Encabezado
        encabezado = ET.SubElement(documento, 'Encabezado')
        
        # ID del documento
        id_doc = ET.SubElement(encabezado, 'IdDoc')
        ET.SubElement(id_doc, 'TipoDTE').text = str(data['tipo_documento'])
        ET.SubElement(id_doc, 'Folio').text = str(data.get('folio', '1'))
        ET.SubElement(id_doc, 'FchEmis').text = self._format_fecha(data.get('fecha_emision'))
        
        # Emisor
        emisor = ET.SubElement(encabezado, 'Emisor')
        ET.SubElement(emisor, 'RUTEmisor').text = data.get('rut_emisor', '')
        ET.SubElement(emisor, 'RznSoc').text = data.get('razon_social_emisor', 'Empresa Emisora')
        
        # Receptor
        receptor = ET.SubElement(encabezado, 'Receptor')
        ET.SubElement(receptor, 'RUTRecep').text = data.get('rut_receptor', '')
        ET.SubElement(receptor, 'RznSocRecep').text = data.get('razon_social_receptor', 'Cliente')
        
        # Totales
        totales = ET.SubElement(encabezado, 'Totales')
        if 'monto_total' in data:
            ET.SubElement(totales, 'MntTotal').text = str(int(data['monto_total']))
        
        # Referencia al documento original
        if data.get('documento_referencia'):
            referencia = ET.SubElement(documento, 'Referencia')
            ET.SubElement(referencia, 'NroLinRef').text = '1'
            ET.SubElement(referencia, 'TpoDocRef').text = str(data['documento_referencia'].get('tipo', '33'))
            ET.SubElement(referencia, 'FolioRef').text = str(data['documento_referencia'].get('folio', ''))
            ET.SubElement(referencia, 'FchRef').text = self._format_fecha(
                data['documento_referencia'].get('fecha')
            )
            ET.SubElement(referencia, 'CodRef').text = str(data['documento_referencia'].get('codigo', '1'))
            ET.SubElement(referencia, 'RazonRef').text = data['documento_referencia'].get(
                'razon', 'Anula documento'
            )
        
        return self._xml_to_string(dte)
    
    def _generate_documento_generico(self, data: Dict[str, Any]) -> str:
        """Genera XML genérico para cualquier tipo de documento."""
        # Crear elemento raíz
        dte = ET.Element('DTE', {
            'xmlns': self._namespaces['dte'],
            'version': '1.0'
        })
        
        # Documento
        documento = ET.SubElement(dte, 'Documento', {'ID': 'DOC' + str(data.get('folio', '1'))})
        
        # Encabezado
        encabezado = ET.SubElement(documento, 'Encabezado')
        
        # ID del documento
        id_doc = ET.SubElement(encabezado, 'IdDoc')
        ET.SubElement(id_doc, 'TipoDTE').text = str(data.get('tipo_documento', '33'))
        ET.SubElement(id_doc, 'Folio').text = str(data.get('folio', '1'))
        ET.SubElement(id_doc, 'FchEmis').text = self._format_fecha(data.get('fecha_emision'))
        
        # Agregar todos los campos disponibles
        for key, value in data.items():
            if key not in ['tipo_documento', 'folio', 'fecha_emision'] and not isinstance(value, (dict, list)):
                elem = ET.SubElement(encabezado, key)
                elem.text = str(value)
        
        return self._xml_to_string(dte)
    
    def _format_fecha(self, fecha: Any) -> str:
        """Formatea una fecha para XML."""
        if isinstance(fecha, str):
            return fecha
        elif isinstance(fecha, date):
            return fecha.strftime(self.config.formato_fecha)
        elif isinstance(fecha, datetime):
            return fecha.strftime(self.config.formato_fecha)
        else:
            return datetime.now().strftime(self.config.formato_fecha)
    
    def _xml_to_string(self, element: ET.Element) -> str:
        """Convierte un elemento XML a string formateado."""
        # Convertir a string sin formato
        xml_str = ET.tostring(element, encoding='unicode')
        
        # Si se requiere indentación, usar minidom
        if self.config.indent:
            dom = minidom.parseString(xml_str)
            return dom.toprettyxml(indent="  ", encoding=None)
        
        return xml_str
    
    def generate_batch(self, documentos: List[Dict[str, Any]]) -> List[str]:
        """
        Genera múltiples documentos XML.
        
        Args:
            documentos: Lista de diccionarios con datos de documentos
            
        Returns:
            List[str]: Lista de XMLs generados
        """
        xmls_generados = []
        
        for documento_data in documentos:
            try:
                xml = self.generate(documento_data)
                xmls_generados.append(xml)
            except Exception as e:
                # En caso de error, agregar un XML de error
                error_xml = self._generate_error_xml(documento_data, str(e))
                xmls_generados.append(error_xml)
        
        return xmls_generados
    
    def _generate_error_xml(self, documento_data: Dict[str, Any], error_msg: str) -> str:
        """Genera un XML de error cuando falla la generación."""
        error = ET.Element('Error')
        ET.SubElement(error, 'Mensaje').text = error_msg
        ET.SubElement(error, 'Documento').text = str(documento_data.get('folio', 'N/A'))
        ET.SubElement(error, 'Tipo').text = str(documento_data.get('tipo_documento', 'N/A'))
        
        return self._xml_to_string(error)
    
    def validate_before_generate(self, documento_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida los datos antes de generar el XML.
        
        Args:
            documento_data: Datos del documento
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_errores)
        """
        errores = []
        
        # Validación básica
        if not isinstance(documento_data, dict):
            errores.append("Los datos deben ser un diccionario")
            return False, errores
        
        # Validar tipo de documento
        tipo_documento = documento_data.get('tipo_documento')
        if not tipo_documento:
            errores.append("Tipo de documento es obligatorio")
        elif str(tipo_documento) not in self._templates:
            errores.append(f"Tipo de documento no soportado: {tipo_documento}")
        
        # Validar campos obligatorios según el tipo
        if tipo_documento and str(tipo_documento) in self._templates:
            template = self._templates[str(tipo_documento)]
            elementos_obligatorios = template.get('elementos_obligatorios', [])
            
            # Mapeo de campos internos a elementos XML
            mapeo_campos = {
                'RUTEmisor': 'rut_emisor',
                'RUTRecep': 'rut_receptor',
                'FchEmis': 'fecha_emision',
                'MntNeto': 'monto_neto',
                'MntExe': 'monto_exento',
                'MntTotal': 'monto_total',
                'DirOrigen': 'direccion_emisor',
                'DirDest': 'direccion_despacho',
                'FolioRef': 'documento_referencia'
            }
            
            for elemento in elementos_obligatorios:
                campo = mapeo_campos.get(elemento, elemento.lower())
                if campo not in documento_data:
                    errores.append(f"Campo obligatorio faltante: {campo}")
        
        es_valido = len(errores) == 0
        return es_valido, errores
    
    def get_template_info(self, tipo_documento: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de la plantilla de un tipo de documento.
        
        Args:
            tipo_documento: Código del tipo de documento
            
        Returns:
            Dict con información de la plantilla o None
        """
        return self._templates.get(str(tipo_documento))
    
    def list_supported_documents(self) -> Dict[str, str]:
        """
        Lista los tipos de documento soportados.
        
        Returns:
            Dict con código y nombre de documentos soportados
        """
        return {codigo: template['nombre'] for codigo, template in self._templates.items()}
