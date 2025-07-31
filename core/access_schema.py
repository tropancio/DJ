"""
Módulo para cargar metadata desde la base de datos Access.
Proporciona funciones para extraer información de tablas DECLARACIONES, CAMPOS y VALIDACIONES.
"""

import pyodbc
import pandas as pd
from typing import Dict, List, Optional, Any
import os
from pathlib import Path


class AccessSchema:
    """Clase para manejar la conexión y consultas a la base de datos Access."""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa la conexión a Access.
        
        Args:
            db_path: Ruta al archivo .accdb. Si no se especifica, usa la ruta por defecto.
        """
        if db_path is None:
            # Ruta por defecto relativa al proyecto
            project_root = Path(__file__).parent.parent
            db_path = project_root / "access_model" / "modelo.accdb"
        
        self.db_path = str(db_path)
        self.connection_string = (
            f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
            f"DBQ={self.db_path};"
        )
        
    def _get_connection(self) -> pyodbc.Connection:
        """Obtiene una conexión a la base de datos Access."""
        try:
            return pyodbc.connect(self.connection_string)
        except pyodbc.Error as e:
            raise ConnectionError(f"Error conectando a Access: {e}")
    
    def get_declaracion_info(self, dj_codigo: str) -> Dict[str, Any]:
        """
        Obtiene información de una declaración específica.
        
        Args:
            dj_codigo: Código de la declaración (ej. "1922")
            
        Returns:
            Diccionario con información de la declaración
        """
        query = """
        SELECT DJ_CODIGO, NOMBRE, TIPO, DESCRIPCION, ACTIVA
        FROM DECLARACIONES 
        WHERE DJ_CODIGO = ?
        """
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (dj_codigo,))
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Declaración {dj_codigo} no encontrada")
            
            return {
                'dj_codigo': row.DJ_CODIGO,
                'nombre': row.NOMBRE,
                'tipo': row.TIPO,  # 'SIMPLE' o 'COMPUESTA'
                'descripcion': row.DESCRIPCION,
                'activa': row.ACTIVA
            }
    
    def get_campos_declaracion(self, dj_codigo: str) -> pd.DataFrame:
        """
        Obtiene todos los campos de una declaración.
        
        Args:
            dj_codigo: Código de la declaración
            
        Returns:
            DataFrame con información de los campos
        """
        query = """
        SELECT 
            CAMPO_ID,
            DJ_CODIGO,
            CODIGO_CAMPO,
            NOMBRE_CAMPO,
            TIPO_DATO,
            LONGITUD,
            DECIMALES,
            OBLIGATORIO,
            POSICION,
            ALINEACION,
            RELLENO,
            FORMATO_EJEMPLO,
            DESCRIPCION,
            SECCION,
            TABLA_LOOKUP
        FROM CAMPOS 
        WHERE DJ_CODIGO = ?
        ORDER BY POSICION
        """
        
        with self._get_connection() as conn:
            return pd.read_sql(query, conn, params=(dj_codigo,))
    
    def get_validaciones_declaracion(self, dj_codigo: str) -> pd.DataFrame:
        """
        Obtiene todas las validaciones de una declaración.
        
        Args:
            dj_codigo: Código de la declaración
            
        Returns:
            DataFrame con información de las validaciones
        """
        query = """
        SELECT 
            VALIDACION_ID,
            CAMPO_ID,
            DJ_CODIGO,
            CODIGO_VALIDACION,
            TIPO_VALIDACION,
            EXPRESION_PY,
            MENSAJE_ERROR,
            ACTIVA
        FROM VALIDACIONES 
        WHERE DJ_CODIGO = ? AND ACTIVA = True
        ORDER BY CAMPO_ID, CODIGO_VALIDACION
        """
        
        with self._get_connection() as conn:
            return pd.read_sql(query, conn, params=(dj_codigo,))
    
    def get_tabla_lookup(self, tabla_nombre: str) -> pd.DataFrame:
        """
        Obtiene datos de una tabla de referencia/lookup.
        
        Args:
            tabla_nombre: Nombre de la tabla (ej. "UF", "CODIGOS_SII")
            
        Returns:
            DataFrame con los datos de la tabla
        """
        # Validar que el nombre de tabla sea seguro (prevenir SQL injection)
        if not tabla_nombre.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Nombre de tabla inválido: {tabla_nombre}")
        
        query = f"SELECT * FROM {tabla_nombre}"
        
        with self._get_connection() as conn:
            return pd.read_sql(query, conn)
    
    def get_metadata_completa(self, dj_codigo: str) -> Dict[str, Any]:
        """
        Obtiene toda la metadata necesaria para una declaración.
        
        Args:
            dj_codigo: Código de la declaración
            
        Returns:
            Diccionario con toda la metadata estructurada
        """
        # Información básica de la declaración
        declaracion_info = self.get_declaracion_info(dj_codigo)
        
        # Campos
        campos_df = self.get_campos_declaracion(dj_codigo)
        
        # Validaciones
        validaciones_df = self.get_validaciones_declaracion(dj_codigo)
        
        # Crear diccionario de campos indexado por código de campo
        campos_dict = {}
        for _, campo in campos_df.iterrows():
            campos_dict[campo['CODIGO_CAMPO']] = {
                'campo_id': campo['CAMPO_ID'],
                'nombre': campo['NOMBRE_CAMPO'],
                'tipo_dato': campo['TIPO_DATO'],
                'longitud': campo['LONGITUD'],
                'decimales': campo['DECIMALES'],
                'obligatorio': campo['OBLIGATORIO'],
                'posicion': campo['POSICION'],
                'alineacion': campo['ALINEACION'],
                'relleno': campo['RELLENO'],
                'formato_ejemplo': campo['FORMATO_EJEMPLO'],
                'descripcion': campo['DESCRIPCION'],
                'seccion': campo['SECCION'],
                'tabla_lookup': campo['TABLA_LOOKUP']
            }
        
        # Crear diccionario de validaciones agrupadas por campo
        validaciones_dict = {}
        for _, validacion in validaciones_df.iterrows():
            campo_id = validacion['CAMPO_ID']
            
            # Buscar el código de campo correspondiente
            codigo_campo = None
            for codigo, info in campos_dict.items():
                if info['campo_id'] == campo_id:
                    codigo_campo = codigo
                    break
            
            if codigo_campo:
                if codigo_campo not in validaciones_dict:
                    validaciones_dict[codigo_campo] = []
                
                validaciones_dict[codigo_campo].append({
                    'codigo_validacion': validacion['CODIGO_VALIDACION'],
                    'tipo_validacion': validacion['TIPO_VALIDACION'],
                    'expresion_py': validacion['EXPRESION_PY'],
                    'mensaje_error': validacion['MENSAJE_ERROR']
                })
        
        return {
            'declaracion': declaracion_info,
            'campos': campos_dict,
            'validaciones': validaciones_dict,
            'campos_df': campos_df,
            'validaciones_df': validaciones_df
        }
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión a la base de datos.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM DECLARACIONES")
                cursor.fetchone()
                return True
        except Exception:
            return False


# Función de conveniencia para uso directo
def obtener_metadata(dj_codigo: str, db_path: str = None) -> Dict[str, Any]:
    """
    Función de conveniencia para obtener metadata de una declaración.
    
    Args:
        dj_codigo: Código de la declaración
        db_path: Ruta opcional al archivo Access
        
    Returns:
        Diccionario con toda la metadata
    """
    schema = AccessSchema(db_path)
    return schema.get_metadata_completa(dj_codigo)


if __name__ == "__main__":
    # Ejemplo de uso
    try:
        schema = AccessSchema()
        if schema.test_connection():
            print("✓ Conexión a Access exitosa")
            
            # Ejemplo con DJ 1922
            metadata = obtener_metadata("1922")
            print(f"✓ Metadata cargada para DJ {metadata['declaracion']['nombre']}")
            print(f"  - Tipo: {metadata['declaracion']['tipo']}")
            print(f"  - Campos: {len(metadata['campos'])}")
            print(f"  - Validaciones: {sum(len(v) for v in metadata['validaciones'].values())}")
        else:
            print("✗ Error en conexión a Access")
    except Exception as e:
        print(f"✗ Error: {e}")
