"""
Módulo para guardar DataFrames validados en la base de datos Access.
Maneja la inserción de datos en tablas de Access con manejo de errores y transacciones.
"""

import pandas as pd
import pyodbc
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from ..access_schema import AccessSchema


class AccessStorage:
    """Manejador de almacenamiento en Access."""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa el manejador de almacenamiento.
        
        Args:
            db_path: Ruta al archivo .accdb. Si no se especifica, usa la ruta por defecto.
        """
        self.access_schema = AccessSchema(db_path)
        self.db_path = self.access_schema.db_path
    
    def guardar_dataframe(self, df: pd.DataFrame, tabla_destino: str, 
                         dj_codigo: str, empresa: Dict[str, Any],
                         batch_size: int = 1000) -> Dict[str, Any]:
        """
        Guarda un DataFrame en una tabla de Access.
        
        Args:
            df: DataFrame a guardar
            tabla_destino: Nombre de la tabla de destino en Access
            dj_codigo: Código de la DJ
            empresa: Datos de la empresa
            batch_size: Tamaño del lote para inserción por bloques
            
        Returns:
            Diccionario con resultado de la operación
        """
        resultado = {
            "exito": False,
            "filas_insertadas": 0,
            "filas_fallidas": 0,
            "errores": [],
            "tiempo_inicio": datetime.now(),
            "tiempo_fin": None,
            "duracion_segundos": None
        }
        
        try:
            with self.access_schema._get_connection() as conn:
                # Iniciar transacción
                conn.autocommit = False
                
                try:
                    # Verificar que la tabla existe
                    self._verificar_tabla(conn, tabla_destino)
                    
                    # Preparar datos con metadatos
                    df_preparado = self._preparar_dataframe(df, dj_codigo, empresa)
                    
                    # Insertar en lotes
                    filas_insertadas = self._insertar_en_lotes(
                        conn, df_preparado, tabla_destino, batch_size
                    )
                    
                    # Confirmar transacción
                    conn.commit()
                    
                    resultado.update({
                        "exito": True,
                        "filas_insertadas": filas_insertadas,
                        "mensaje": f"Se insertaron {filas_insertadas} filas exitosamente"
                    })
                    
                except Exception as e:
                    # Revertir transacción en caso de error
                    conn.rollback()
                    resultado["errores"].append(f"Error en transacción: {str(e)}")
                    raise
                
        except Exception as e:
            resultado["errores"].append(f"Error de conexión: {str(e)}")
        
        finally:
            resultado["tiempo_fin"] = datetime.now()
            resultado["duracion_segundos"] = (
                resultado["tiempo_fin"] - resultado["tiempo_inicio"]
            ).total_seconds()
        
        return resultado
    
    def _verificar_tabla(self, conn: pyodbc.Connection, tabla_destino: str) -> None:
        """Verifica que la tabla de destino existe en Access."""
        cursor = conn.cursor()
        try:
            # Intentar una consulta simple para verificar existencia
            cursor.execute(f"SELECT TOP 1 * FROM {tabla_destino}")
        except pyodbc.Error:
            raise ValueError(f"La tabla '{tabla_destino}' no existe en la base de datos")
    
    def _preparar_dataframe(self, df: pd.DataFrame, dj_codigo: str, 
                           empresa: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepara el DataFrame agregando columnas de metadatos.
        
        Args:
            df: DataFrame original
            dj_codigo: Código de la DJ
            empresa: Datos de la empresa
            
        Returns:
            DataFrame preparado con metadatos
        """
        df_preparado = df.copy()
        
        # Agregar columnas de metadatos
        df_preparado['DJ_CODIGO'] = dj_codigo
        df_preparado['RUT_EMPRESA'] = empresa.get('rut', '')
        df_preparado['NOMBRE_EMPRESA'] = empresa.get('nombre', '')
        df_preparado['FECHA_CARGA'] = datetime.now()
        df_preparado['USUARIO_CARGA'] = empresa.get('usuario', 'SISTEMA')
        df_preparado['ESTADO'] = 'CARGADO'
        
        # Generar ID único para cada fila
        df_preparado['ID_REGISTRO'] = [
            f"{dj_codigo}_{empresa.get('rut', '')}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i:06d}"
            for i in range(len(df_preparado))
        ]
        
        return df_preparado
    
    def _insertar_en_lotes(self, conn: pyodbc.Connection, df: pd.DataFrame, 
                          tabla_destino: str, batch_size: int) -> int:
        """
        Inserta DataFrame en lotes para mejor rendimiento.
        
        Args:
            conn: Conexión a Access
            df: DataFrame a insertar
            tabla_destino: Tabla de destino
            batch_size: Tamaño del lote
            
        Returns:
            Número total de filas insertadas
        """
        cursor = conn.cursor()
        total_insertadas = 0
        
        # Obtener nombres de columnas
        columnas = list(df.columns)
        placeholders = ', '.join(['?' for _ in columnas])
        
        # Construir query de inserción
        query_insert = f"""
        INSERT INTO {tabla_destino} ({', '.join(columnas)})
        VALUES ({placeholders})
        """
        
        # Procesar en lotes
        for i in range(0, len(df), batch_size):
            lote = df.iloc[i:i + batch_size]
            
            # Convertir lote a lista de tuplas
            datos_lote = []
            for _, fila in lote.iterrows():
                # Convertir valores pandas a tipos nativos de Python
                fila_convertida = []
                for valor in fila:
                    if pd.isna(valor):
                        fila_convertida.append(None)
                    elif isinstance(valor, pd.Timestamp):
                        fila_convertida.append(valor.to_pydatetime())
                    else:
                        fila_convertida.append(valor)
                
                datos_lote.append(tuple(fila_convertida))
            
            # Insertar lote
            cursor.executemany(query_insert, datos_lote)
            total_insertadas += len(datos_lote)
        
        return total_insertadas
    
    def crear_tabla_dinamica(self, df: pd.DataFrame, nombre_tabla: str, 
                            dj_codigo: str) -> Dict[str, Any]:
        """
        Crea una tabla dinámicamente basada en la estructura del DataFrame.
        
        Args:
            df: DataFrame de referencia
            nombre_tabla: Nombre de la nueva tabla
            dj_codigo: Código de la DJ
            
        Returns:
            Diccionario con resultado de la operación
        """
        resultado = {
            "exito": False,
            "tabla_creada": nombre_tabla,
            "columnas_creadas": [],
            "errores": []
        }
        
        try:
            with self.access_schema._get_connection() as conn:
                cursor = conn.cursor()
                
                # Construir DDL para crear tabla
                ddl = self._generar_ddl_tabla(df, nombre_tabla, dj_codigo)
                
                # Ejecutar DDL
                cursor.execute(ddl)
                conn.commit()
                
                resultado.update({
                    "exito": True,
                    "columnas_creadas": list(df.columns),
                    "mensaje": f"Tabla '{nombre_tabla}' creada exitosamente"
                })
                
        except Exception as e:
            resultado["errores"].append(f"Error creando tabla: {str(e)}")
        
        return resultado
    
    def _generar_ddl_tabla(self, df: pd.DataFrame, nombre_tabla: str, 
                          dj_codigo: str) -> str:
        """
        Genera DDL para crear tabla basada en tipos de datos del DataFrame.
        
        Args:
            df: DataFrame de referencia
            nombre_tabla: Nombre de la tabla
            dj_codigo: Código de la DJ
            
        Returns:
            String con DDL de creación de tabla
        """
        columnas_ddl = []
        
        # Mapeo de tipos pandas a tipos Access/SQL
        tipo_mapping = {
            'object': 'TEXT(255)',
            'int64': 'INTEGER',
            'float64': 'DOUBLE',
            'bool': 'YESNO',
            'datetime64[ns]': 'DATETIME'
        }
        
        # Procesar columnas del DataFrame
        for columna in df.columns:
            tipo_pandas = str(df[columna].dtype)
            tipo_access = tipo_mapping.get(tipo_pandas, 'TEXT(255)')
            
            # Ajustar longitud para campos de texto basado en datos
            if tipo_pandas == 'object':
                max_length = df[columna].astype(str).str.len().max()
                if pd.notna(max_length) and max_length > 0:
                    longitud_sugerida = min(max(max_length * 2, 50), 255)
                    tipo_access = f'TEXT({longitud_sugerida})'
            
            columnas_ddl.append(f'[{columna}] {tipo_access}')
        
        # Agregar columnas de metadatos
        columnas_metadatos = [
            '[DJ_CODIGO] TEXT(10)',
            '[RUT_EMPRESA] TEXT(12)',
            '[NOMBRE_EMPRESA] TEXT(255)',
            '[FECHA_CARGA] DATETIME',
            '[USUARIO_CARGA] TEXT(50)',
            '[ESTADO] TEXT(20)',
            '[ID_REGISTRO] TEXT(100) PRIMARY KEY'
        ]
        
        columnas_ddl.extend(columnas_metadatos)
        
        # Construir DDL completo
        ddl = f"""
        CREATE TABLE [{nombre_tabla}] (
            {', '.join(columnas_ddl)}
        )
        """
        
        return ddl
    
    def obtener_estadisticas_tabla(self, tabla: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas de una tabla en Access.
        
        Args:
            tabla: Nombre de la tabla
            
        Returns:
            Diccionario con estadísticas
        """
        estadisticas = {
            "tabla": tabla,
            "total_registros": 0,
            "columnas": [],
            "fecha_consulta": datetime.now(),
            "errores": []
        }
        
        try:
            with self.access_schema._get_connection() as conn:
                cursor = conn.cursor()
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM [{tabla}]")
                estadisticas["total_registros"] = cursor.fetchone()[0]
                
                # Obtener información de columnas
                cursor.execute(f"SELECT TOP 1 * FROM [{tabla}]")
                estadisticas["columnas"] = [desc[0] for desc in cursor.description]
                
                # Estadísticas por DJ si aplica
                if 'DJ_CODIGO' in estadisticas["columnas"]:
                    cursor.execute(f"""
                        SELECT DJ_CODIGO, COUNT(*) as CANTIDAD
                        FROM [{tabla}]
                        GROUP BY DJ_CODIGO
                    """)
                    estadisticas["por_dj"] = {
                        row[0]: row[1] for row in cursor.fetchall()
                    }
                
        except Exception as e:
            estadisticas["errores"].append(f"Error obteniendo estadísticas: {str(e)}")
        
        return estadisticas
    
    def limpiar_tabla(self, tabla: str, dj_codigo: str = None, 
                     rut_empresa: str = None) -> Dict[str, Any]:
        """
        Limpia registros de una tabla con filtros opcionales.
        
        Args:
            tabla: Nombre de la tabla
            dj_codigo: Filtro opcional por DJ
            rut_empresa: Filtro opcional por RUT empresa
            
        Returns:
            Diccionario con resultado de la operación
        """
        resultado = {
            "exito": False,
            "registros_eliminados": 0,
            "errores": []
        }
        
        try:
            with self.access_schema._get_connection() as conn:
                cursor = conn.cursor()
                
                # Construir WHERE clause
                where_conditions = []
                params = []
                
                if dj_codigo:
                    where_conditions.append("DJ_CODIGO = ?")
                    params.append(dj_codigo)
                
                if rut_empresa:
                    where_conditions.append("RUT_EMPRESA = ?")
                    params.append(rut_empresa)
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Contar registros antes de eliminar
                count_query = f"SELECT COUNT(*) FROM [{tabla}] {where_clause}"
                cursor.execute(count_query, params)
                registros_a_eliminar = cursor.fetchone()[0]
                
                if registros_a_eliminar > 0:
                    # Eliminar registros
                    delete_query = f"DELETE FROM [{tabla}] {where_clause}"
                    cursor.execute(delete_query, params)
                    conn.commit()
                    
                    resultado.update({
                        "exito": True,
                        "registros_eliminados": registros_a_eliminar,
                        "mensaje": f"Se eliminaron {registros_a_eliminar} registros"
                    })
                else:
                    resultado.update({
                        "exito": True,
                        "registros_eliminados": 0,
                        "mensaje": "No se encontraron registros para eliminar"
                    })
                
        except Exception as e:
            resultado["errores"].append(f"Error en limpieza: {str(e)}")
        
        return resultado


def guardar_dj_access(df: pd.DataFrame, dj_codigo: str, empresa: Dict[str, Any],
                     tabla_destino: str = None, db_path: str = None) -> Dict[str, Any]:
    """
    Función de conveniencia para guardar DataFrame de DJ en Access.
    
    Args:
        df: DataFrame validado a guardar
        dj_codigo: Código de la declaración jurada
        empresa: Datos de la empresa
        tabla_destino: Tabla de destino (si no se especifica, usa patrón DJ_AAAA)
        db_path: Ruta opcional al archivo Access
        
    Returns:
        Resultado de la operación
    """
    if tabla_destino is None:
        tabla_destino = f"DJ_{dj_codigo}"
    
    storage = AccessStorage(db_path)
    return storage.guardar_dataframe(df, tabla_destino, dj_codigo, empresa)


if __name__ == "__main__":
    # Ejemplo de uso
    import pandas as pd
    
    # Datos de ejemplo
    df_ejemplo = pd.DataFrame({
        'C1': ['12345678-9', '98765432-1'],
        'C2': [1000000, 2500000],
        'C3': ['EMPRESA A', 'EMPRESA B']
    })
    
    # Datos de empresa
    empresa_ejemplo = {
        'rut': '76123456-7',
        'nombre': 'EMPRESA DE PRUEBA S.A.',
        'usuario': 'admin'
    }
    
    try:
        print("Guardando datos en Access...")
        resultado = guardar_dj_access(df_ejemplo, "1922", empresa_ejemplo)
        
        if resultado["exito"]:
            print(f"✓ Guardado exitoso: {resultado['filas_insertadas']} filas")
            print(f"✓ Duración: {resultado['duracion_segundos']:.2f} segundos")
        else:
            print("✗ Error guardando datos:")
            for error in resultado["errores"]:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"✗ Error: {e}")
