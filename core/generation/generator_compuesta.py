"""
Módulo para generar archivos de salida para Declaraciones Juradas compuestas.
Maneja la combinación de múltiples secciones en una tabla final.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from .generator_simple import GeneratorSimple
from ..access_schema import AccessSchema, obtener_metadata


class GeneratorCompuesta:
    """Generador de archivos para DJs compuestas."""
    
    def __init__(self, metadata: Dict[str, Any], empresa: Dict[str, Any]):
        """
        Inicializa el generador con metadata y datos de empresa.
        
        Args:
            metadata: Metadata completa de la DJ obtenida de Access
            empresa: Diccionario con datos de la empresa
        """
        self.metadata = metadata
        self.empresa = empresa
        self.dj_codigo = metadata['declaracion']['dj_codigo']
        self.campos = metadata['campos']
        
        # Obtener extensión del archivo
        self.extension = self.dj_codigo[-3:] if len(self.dj_codigo) >= 3 else self.dj_codigo
        
        # Agrupar campos por sección
        self.secciones = self._obtener_secciones()
        self.campos_por_seccion = self._agrupar_campos_por_seccion()
    
    def consolidar_dataframes(self, dataframes_secciones: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Consolida múltiples DataFrames de secciones en uno final.
        
        Args:
            dataframes_secciones: Diccionario {nombre_seccion: DataFrame}
            
        Returns:
            DataFrame consolidado con todas las secciones
        """
        # Verificar que todas las secciones estén presentes
        secciones_faltantes = set(self.secciones) - set(dataframes_secciones.keys())
        if secciones_faltantes:
            raise ValueError(f"Faltan secciones: {', '.join(secciones_faltantes)}")
        
        # Determinar estrategia de consolidación
        return self._consolidar_por_concatenacion(dataframes_secciones)
    
    def _consolidar_por_concatenacion(self, dataframes_secciones: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Consolida DataFrames concatenando columnas (estrategia más común).
        Asume que todas las secciones tienen el mismo número de filas.
        """
        # Verificar que todos los DataFrames tengan el mismo número de filas
        num_filas = None
        for seccion, df in dataframes_secciones.items():
            if num_filas is None:
                num_filas = len(df)
            elif len(df) != num_filas:
                raise ValueError(f"Sección '{seccion}' tiene {len(df)} filas, se esperaban {num_filas}")
        
        # Concatenar por columnas en orden de sección
        dataframes_ordenados = []
        for seccion in self.secciones:
            if seccion in dataframes_secciones:
                dataframes_ordenados.append(dataframes_secciones[seccion])
        
        # Concatenar horizontalmente
        df_consolidado = pd.concat(dataframes_ordenados, axis=1)
        
        return df_consolidado
    
    def _consolidar_por_union(self, dataframes_secciones: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Alternativa: Consolida DataFrames por unión vertical (menos común).
        Útil cuando las secciones representan diferentes tipos de registros.
        """
        # Obtener todas las columnas únicas
        todas_columnas = set()
        for df in dataframes_secciones.values():
            todas_columnas.update(df.columns)
        
        # Normalizar DataFrames para que tengan las mismas columnas
        dataframes_normalizados = []
        for seccion, df in dataframes_secciones.items():
            df_normalizado = df.copy()
            for columna in todas_columnas:
                if columna not in df_normalizado.columns:
                    df_normalizado[columna] = None
            
            # Agregar columna identificadora de sección
            df_normalizado['_SECCION'] = seccion
            dataframes_normalizados.append(df_normalizado)
        
        # Concatenar verticalmente
        df_consolidado = pd.concat(dataframes_normalizados, axis=0, ignore_index=True)
        
        return df_consolidado
    
    def generar_archivo(self, dataframes_secciones: Dict[str, pd.DataFrame], 
                       output_path: str = None) -> str:
        """
        Genera el archivo de salida a partir de DataFrames de secciones.
        
        Args:
            dataframes_secciones: Diccionario {nombre_seccion: DataFrame}
            output_path: Ruta donde guardar el archivo
            
        Returns:
            Ruta del archivo generado
        """
        # Consolidar DataFrames
        df_consolidado = self.consolidar_dataframes(dataframes_secciones)
        
        # Usar el generador simple para crear el archivo
        generator_simple = GeneratorSimple(self.metadata, self.empresa)
        return generator_simple.generar_archivo(df_consolidado, output_path)
    
    def _obtener_secciones(self) -> List[str]:
        """Obtiene lista única de secciones ordenadas."""
        secciones = set()
        for info_campo in self.campos.values():
            if info_campo['seccion']:
                secciones.add(info_campo['seccion'])
        
        return sorted(list(secciones))
    
    def _agrupar_campos_por_seccion(self) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa campos por sección."""
        campos_por_seccion = {}
        
        for codigo_campo, info_campo in self.campos.items():
            seccion = info_campo['seccion']
            if seccion:
                if seccion not in campos_por_seccion:
                    campos_por_seccion[seccion] = []
                
                campos_por_seccion[seccion].append({
                    'codigo': codigo_campo,
                    'info': info_campo
                })
        
        # Ordenar campos dentro de cada sección por posición
        for seccion in campos_por_seccion:
            campos_por_seccion[seccion].sort(key=lambda x: x['info']['posicion'])
        
        return campos_por_seccion
    
    def validar_estructura_secciones(self, dataframes_secciones: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Valida la estructura de los DataFrames de secciones antes de consolidar.
        
        Args:
            dataframes_secciones: Diccionario {nombre_seccion: DataFrame}
            
        Returns:
            Diccionario con resultado de validación
        """
        resultado = {
            "valido": True,
            "errores": [],
            "advertencias": [],
            "resumen_secciones": {}
        }
        
        # Verificar secciones requeridas
        secciones_faltantes = set(self.secciones) - set(dataframes_secciones.keys())
        if secciones_faltantes:
            resultado["valido"] = False
            resultado["errores"].append(f"Faltan secciones: {', '.join(secciones_faltantes)}")
        
        # Verificar secciones extra
        secciones_extra = set(dataframes_secciones.keys()) - set(self.secciones)
        if secciones_extra:
            resultado["advertencias"].append(f"Secciones no esperadas: {', '.join(secciones_extra)}")
        
        # Validar cada sección
        num_filas_referencia = None
        for seccion, df in dataframes_secciones.items():
            info_seccion = {
                "num_filas": len(df),
                "num_columnas": len(df.columns),
                "columnas": list(df.columns)
            }
            
            # Verificar que todas las secciones tengan el mismo número de filas
            if num_filas_referencia is None:
                num_filas_referencia = len(df)
            elif len(df) != num_filas_referencia:
                resultado["valido"] = False
                resultado["errores"].append(
                    f"Sección '{seccion}' tiene {len(df)} filas, "
                    f"pero se esperaban {num_filas_referencia}"
                )
            
            # Verificar columnas esperadas para esta sección
            if seccion in self.campos_por_seccion:
                columnas_esperadas = [campo['codigo'] for campo in self.campos_por_seccion[seccion]]
                columnas_faltantes = set(columnas_esperadas) - set(df.columns)
                columnas_extra = set(df.columns) - set(columnas_esperadas)
                
                if columnas_faltantes:
                    resultado["errores"].append(
                        f"Sección '{seccion}' - faltan columnas: {', '.join(columnas_faltantes)}"
                    )
                
                if columnas_extra:
                    resultado["advertencias"].append(
                        f"Sección '{seccion}' - columnas extra: {', '.join(columnas_extra)}"
                    )
                
                info_seccion["columnas_esperadas"] = columnas_esperadas
                info_seccion["columnas_faltantes"] = list(columnas_faltantes)
                info_seccion["columnas_extra"] = list(columnas_extra)
            
            resultado["resumen_secciones"][seccion] = info_seccion
        
        return resultado
    
    def generar_resumen_compuesto(self, dataframes_secciones: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Genera un resumen completo de la DJ compuesta.
        
        Args:
            dataframes_secciones: Diccionario {nombre_seccion: DataFrame}
            
        Returns:
            Diccionario con información detallada del resumen
        """
        # Consolidar para obtener DataFrame final
        df_consolidado = self.consolidar_dataframes(dataframes_secciones)
        
        # Usar el generador simple para obtener resumen básico
        generator_simple = GeneratorSimple(self.metadata, self.empresa)
        resumen_basico = generator_simple.generar_resumen(df_consolidado)
        
        # Agregar información específica de DJ compuesta
        resumen_secciones = {}
        for seccion, df in dataframes_secciones.items():
            resumen_secciones[seccion] = {
                'num_filas': len(df),
                'num_columnas': len(df.columns),
                'columnas': list(df.columns),
                'campos_esperados': len(self.campos_por_seccion.get(seccion, []))
            }
        
        resumen_completo = {
            **resumen_basico,
            'tipo_dj': 'COMPUESTA',
            'num_secciones': len(self.secciones),
            'secciones': self.secciones,
            'resumen_por_seccion': resumen_secciones,
            'df_consolidado_columnas': len(df_consolidado.columns),
            'estrategia_consolidacion': 'CONCATENACION'
        }
        
        return resumen_completo


def generar_archivo_compuesto(dataframes_secciones: Dict[str, pd.DataFrame], 
                             dj_codigo: str, empresa: Dict[str, Any],
                             output_path: str = None, db_path: str = None) -> str:
    """
    Función de conveniencia para generar archivo de DJ compuesta.
    
    Args:
        dataframes_secciones: Diccionario {nombre_seccion: DataFrame}
        dj_codigo: Código de la declaración jurada
        empresa: Diccionario con datos de la empresa
        output_path: Ruta donde guardar el archivo
        db_path: Ruta opcional al archivo Access
        
    Returns:
        Ruta del archivo generado
    """
    # Obtener metadata
    metadata = obtener_metadata(dj_codigo, db_path)
    
    # Verificar que sea una DJ compuesta
    if metadata['declaracion']['tipo'] != 'COMPUESTA':
        raise ValueError(f"DJ {dj_codigo} no es de tipo COMPUESTA")
    
    # Crear generador y generar archivo
    generator = GeneratorCompuesta(metadata, empresa)
    return generator.generar_archivo(dataframes_secciones, output_path)


def validar_y_generar_compuesto(dataframes_secciones: Dict[str, pd.DataFrame],
                               dj_codigo: str, empresa: Dict[str, Any],
                               output_path: str = None, db_path: str = None) -> Dict[str, Any]:
    """
    Valida la estructura y genera archivo para DJ compuesta.
    
    Args:
        dataframes_secciones: Diccionario {nombre_seccion: DataFrame}
        dj_codigo: Código de la declaración jurada
        empresa: Diccionario con datos de la empresa
        output_path: Ruta donde guardar el archivo
        db_path: Ruta opcional al archivo Access
        
    Returns:
        Diccionario con resultado de la operación
    """
    # Obtener metadata
    metadata = obtener_metadata(dj_codigo, db_path)
    
    # Crear generador
    generator = GeneratorCompuesta(metadata, empresa)
    
    # Validar estructura
    validacion = generator.validar_estructura_secciones(dataframes_secciones)
    
    resultado = {
        "validacion_estructura": validacion,
        "archivo_generado": None,
        "resumen": None,
        "exito": False
    }
    
    if validacion["valido"]:
        try:
            # Generar archivo
            archivo_generado = generator.generar_archivo(dataframes_secciones, output_path)
            
            # Generar resumen
            resumen = generator.generar_resumen_compuesto(dataframes_secciones)
            
            resultado.update({
                "archivo_generado": archivo_generado,
                "resumen": resumen,
                "exito": True
            })
            
        except Exception as e:
            resultado["error_generacion"] = str(e)
    
    return resultado


if __name__ == "__main__":
    # Ejemplo de uso
    import pandas as pd
    
    # Datos de ejemplo para DJ compuesta
    df_seccion1 = pd.DataFrame({
        'C1': ['12345678-9', '98765432-1'],
        'C2': ['EMPRESA A', 'EMPRESA B']
    })
    
    df_seccion2 = pd.DataFrame({
        'C3': [1000000, 2500000],
        'C4': [150000, 375000]
    })
    
    dataframes_secciones = {
        'SECCION_1': df_seccion1,
        'SECCION_2': df_seccion2
    }
    
    # Datos de empresa
    empresa_ejemplo = {
        'rut': '76123456-7',
        'nombre': 'EMPRESA DE PRUEBA S.A.',
        'giro': 'Servicios tecnológicos'
    }
    
    try:
        print("Validando y generando archivo para DJ compuesta...")
        resultado = validar_y_generar_compuesto(
            dataframes_secciones, 
            "1922",  # Cambiar por una DJ compuesta real
            empresa_ejemplo
        )
        
        if resultado["exito"]:
            print(f"✓ Archivo generado: {resultado['archivo_generado']}")
            print(f"✓ Secciones procesadas: {resultado['resumen']['num_secciones']}")
        else:
            print("✗ Error en validación:")
            for error in resultado["validacion_estructura"]["errores"]:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"✗ Error: {e}")
