"""
Tests para el módulo storage.
"""

import pytest
import datetime
from dj.storage import DataGenerar, DataDeclaracion, DataSii


class TestDataGenerar:
    """Tests para la clase DataGenerar."""
    
    def test_store_documento(self):
        """Test almacenar documento."""
        data_gen = DataGenerar()
        
        documento_data = {
            'tipo_documento': '33',
            'rut_emisor': '12345678-9',
            'rut_receptor': '87654321-0',
            'fecha_emision': '2024-01-15',
            'datos': {'monto_total': 100000}
        }
        
        doc_id = data_gen.store(documento_data)
        assert doc_id is not None
        assert data_gen.count() == 1
    
    def test_get_documento(self):
        """Test recuperar documento."""
        data_gen = DataGenerar()
        
        documento_data = {
            'tipo_documento': '33',
            'rut_emisor': '12345678-9',
            'rut_receptor': '87654321-0',
            'fecha_emision': datetime.date(2024, 1, 15),
            'datos': {'monto_total': 100000}
        }
        
        doc_id = data_gen.store(documento_data)
        documento = data_gen.get(doc_id)
        
        assert documento is not None
        assert documento.tipo_documento == '33'
        assert documento.rut_emisor == '12345678-9'
    
    def test_get_by_rut_emisor(self):
        """Test recuperar documentos por RUT emisor."""
        data_gen = DataGenerar()
        
        # Agregar documentos del mismo emisor
        for i in range(3):
            documento_data = {
                'tipo_documento': '33',
                'rut_emisor': '12345678-9',
                'rut_receptor': f'8765432{i}-0',
                'fecha_emision': '2024-01-15',
                'datos': {'monto_total': 100000 + i}
            }
            data_gen.store(documento_data)
        
        documentos = data_gen.get_by_rut_emisor('12345678-9')
        assert len(documentos) == 3


class TestDataDeclaracion:
    """Tests para la clase DataDeclaracion."""
    
    def test_store_declaracion(self):
        """Test almacenar declaración."""
        data_decl = DataDeclaracion()
        
        declaracion_data = {
            'folio': 'F001-123',
            'periodo': '202401',
            'tipo_declaracion': 'F29',
            'rut_declarante': '12345678-9',
            'fecha_declaracion': '2024-01-15',
            'monto_total': 500000
        }
        
        folio = data_decl.store(declaracion_data)
        assert folio == 'F001-123'
        assert data_decl.count() == 1
    
    def test_get_declaracion(self):
        """Test recuperar declaración."""
        data_decl = DataDeclaracion()
        
        declaracion_data = {
            'folio': 'F001-123',
            'periodo': '202401',
            'tipo_declaracion': 'F29',
            'rut_declarante': '12345678-9',
            'fecha_declaracion': datetime.date(2024, 1, 15),
            'monto_total': 500000
        }
        
        folio = data_decl.store(declaracion_data)
        declaracion = data_decl.get(folio)
        
        assert declaracion is not None
        assert declaracion.folio == 'F001-123'
        assert declaracion.monto_total == 500000
    
    def test_get_by_periodo(self):
        """Test recuperar declaraciones por período."""
        data_decl = DataDeclaracion()
        
        # Agregar declaraciones del mismo período
        for i in range(2):
            declaracion_data = {
                'folio': f'F00{i+1}-123',
                'periodo': '202401',
                'tipo_declaracion': 'F29',
                'rut_declarante': f'1234567{i}-9',
                'fecha_declaracion': '2024-01-15',
                'monto_total': 500000 + i
            }
            data_decl.store(declaracion_data)
        
        declaraciones = data_decl.get_by_periodo('202401')
        assert len(declaraciones) == 2


class TestDataSii:
    """Tests para la clase DataSii."""
    
    def test_validar_rut(self):
        """Test validación de RUT."""
        data_sii = DataSii()
        
        # RUT válido
        resultado = data_sii.validar_rut('12345678-5')
        assert resultado['valido'] is True
        
        # RUT inválido
        resultado = data_sii.validar_rut('12345678-0')
        assert resultado['valido'] is False
    
    def test_get_tipo_documento(self):
        """Test obtener tipo de documento."""
        data_sii = DataSii()
        
        tipo_doc = data_sii.get_tipo_documento('33')
        assert tipo_doc is not None
        assert 'Factura Electrónica' in tipo_doc['nombre']
        
        # Tipo no existe
        tipo_doc = data_sii.get_tipo_documento('999')
        assert tipo_doc is None
