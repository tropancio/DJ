"""
Módulo para generar archivos de salida para Declaraciones Juradas simples.
Convierte DataFrames validados en archivos de texto plano con formato específico del SII.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
import re
from datetime import datetime
from ..access_schema import AccessSchema, obtener_metadata


class GeneratorSimple:
    """Generador de archivos para DJs simples."""
    
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
        
        # Obtener últimos 3 dígitos para extensión del archivo
        self.extension = self.dj_codigo[-3:] if len(self.dj_codigo) >= 3 else self.dj_codigo
    
    def generar_archivo(self, df: pd.DataFrame, output_path: str = None) -> str:
        """
        Genera el archivo de salida a partir del DataFrame validado.
        
        Args:
            df: DataFrame validado con los datos
            output_path: Ruta donde guardar el archivo. Si no se especifica, usa nombre por defecto.
            
        Returns:
            Ruta del archivo generado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"DJ{self.dj_codigo}_{timestamp}.{self.extension}"
        
        # Obtener campos ordenados por posición
        campos_ordenados = self._obtener_campos_ordenados()
        
        # Generar líneas del archivo
        lineas = []
        for _, fila in df.iterrows():
            linea = self._generar_linea(fila, campos_ordenados)
            lineas.append(linea)
        
        # Escribir archivo
        with open(output_path, 'w', encoding='latin-1') as f:
            for linea in lineas:
                f.write(linea + '\n')
        
        return output_path
    
    def _obtener_campos_ordenados(self) -> List[Dict[str, Any]]:
        """Obtiene lista de campos ordenados por posición para el archivo de salida."""
        campos_lista = []
        for codigo_campo, info_campo in self.campos.items():
            campos_lista.append({
                'codigo': codigo_campo,
                'info': info_campo
            })
        
        return sorted(campos_lista, key=lambda x: x['info']['posicion'])
    
    def _generar_linea(self, fila: pd.Series, campos_ordenados: List[Dict[str, Any]]) -> str:
        """
        Genera una línea del archivo a partir de una fila del DataFrame.
        
        Args:
            fila: Serie de pandas con los datos de la fila
            campos_ordenados: Lista de campos ordenados por posición
            
        Returns:
            Línea formateada para el archivo
        """
        partes_linea = []
        
        for campo in campos_ordenados:
            codigo_campo = campo['codigo']
            info_campo = campo['info']
            
            # Obtener valor de la fila
            valor = fila.get(codigo_campo, '')
            
            # Formatear el valor según las especificaciones del campo
            valor_formateado = self._formatear_valor(valor, info_campo)
            
            partes_linea.append(valor_formateado)
        
        return ''.join(partes_linea)
    
    def _formatear_valor(self, valor: Any, info_campo: Dict[str, Any]) -> str:
        """
        Formatea un valor según las especificaciones del campo.
        
        Args:
            valor: Valor a formatear
            info_campo: Información del campo con longitud, tipo, alineación, etc.
            
        Returns:
            Valor formateado como string
        """
        # Convertir a string y manejar valores nulos
        if pd.isna(valor) or valor is None:
            valor_str = ''
        else:
            valor_str = str(valor)
        
        # Obtener parámetros de formato
        longitud = info_campo.get('longitud', 0)
        tipo_dato = info_campo.get('tipo_dato', 'TEXT')
        alineacion = info_campo.get('alineacion', 'LEFT')  # LEFT, RIGHT, CENTER
        relleno = info_campo.get('relleno', ' ')  # Carácter de relleno
        decimales = info_campo.get('decimales', 0)
        
        # Formatear según tipo de dato
        if tipo_dato in ['INTEGER', 'NUMERIC']:
            valor_formateado = self._formatear_numerico(valor_str, decimales, longitud, relleno, alineacion)
        elif tipo_dato == 'DECIMAL':
            valor_formateado = self._formatear_decimal(valor_str, decimales, longitud, relleno, alineacion)
        elif tipo_dato == 'DATE':
            valor_formateado = self._formatear_fecha(valor_str, longitud, relleno, alineacion)
        else:  # TEXT, VARCHAR, CHAR
            valor_formateado = self._formatear_texto(valor_str, longitud, relleno, alineacion)
        
        return valor_formateado
    
    def _formatear_numerico(self, valor_str: str, decimales: int, longitud: int, relleno: str, alineacion: str) -> str:
        """Formatea un valor numérico entero."""
        if not valor_str or valor_str == '':
            numero = 0
        else:
            try:
                numero = int(float(valor_str))  # Convertir a float primero para manejar "123.0"
            except (ValueError, TypeError):
                numero = 0
        
        # Convertir a string
        numero_str = str(numero)
        
        # Aplicar alineación y relleno
        return self._aplicar_alineacion(numero_str, longitud, relleno, alineacion)
    
    def _formatear_decimal(self, valor_str: str, decimales: int, longitud: int, relleno: str, alineacion: str) -> str:
        """Formatea un valor decimal."""
        if not valor_str or valor_str == '':
            numero = 0.0
        else:
            try:
                numero = float(valor_str)
            except (ValueError, TypeError):
                numero = 0.0
        
        # Formatear con decimales específicos
        if decimales > 0:
            formato = f"{{:.{decimales}f}}"
            numero_str = formato.format(numero)
            # Remover punto decimal y rellenar con ceros si es necesario
            numero_str = numero_str.replace('.', '').zfill(longitud)
        else:
            numero_str = str(int(numero))
        
        # Aplicar alineación y relleno
        return self._aplicar_alineacion(numero_str, longitud, relleno, alineacion)
    
    def _formatear_fecha(self, valor_str: str, longitud: int, relleno: str, alineacion: str) -> str:
        """Formatea una fecha."""
        if not valor_str or valor_str == '':
            fecha_str = ''
        else:
            try:
                # Intentar parsear diferentes formatos de fecha
                if isinstance(valor_str, str):
                    # Formato YYYY-MM-DD
                    if re.match(r'\d{4}-\d{2}-\d{2}', valor_str):
                        fecha_str = valor_str.replace('-', '')
                    # Formato DD/MM/YYYY
                    elif re.match(r'\d{2}/\d{2}/\d{4}', valor_str):
                        partes = valor_str.split('/')
                        fecha_str = f"{partes[2]}{partes[1]}{partes[0]}"
                    # Formato DD-MM-YYYY
                    elif re.match(r'\d{2}-\d{2}-\d{4}', valor_str):
                        partes = valor_str.split('-')
                        fecha_str = f"{partes[2]}{partes[1]}{partes[0]}"
                    else:
                        fecha_str = valor_str
                else:
                    fecha_str = str(valor_str)
            except Exception:
                fecha_str = str(valor_str)
        
        # Aplicar alineación y relleno
        return self._aplicar_alineacion(fecha_str, longitud, relleno, alineacion)
    
    def _formatear_texto(self, valor_str: str, longitud: int, relleno: str, alineacion: str) -> str:
        """Formatea un valor de texto."""
        # Limpiar el texto (remover caracteres especiales si es necesario)
        texto_limpio = valor_str.strip()
        
        # Truncar si es demasiado largo
        if len(texto_limpio) > longitud:
            texto_limpio = texto_limpio[:longitud]
        
        # Aplicar alineación y relleno
        return self._aplicar_alineacion(texto_limpio, longitud, relleno, alineacion)
    
    def _aplicar_alineacion(self, valor_str: str, longitud: int, relleno: str, alineacion: str) -> str:
        """
        Aplica alineación y relleno a un string.
        
        Args:
            valor_str: String a formatear
            longitud: Longitud final deseada
            relleno: Carácter de relleno
            alineacion: Tipo de alineación (LEFT, RIGHT, CENTER)
            
        Returns:
            String formateado con la longitud especificada
        """
        if longitud <= 0:
            return valor_str
        
        # Asegurar que el carácter de relleno sea válido
        if not relleno or len(relleno) != 1:
            relleno = ' '
        
        # Truncar si es demasiado largo
        if len(valor_str) > longitud:
            valor_str = valor_str[:longitud]
        
        # Aplicar alineación
        if alineacion == 'RIGHT':
            return valor_str.rjust(longitud, relleno)
        elif alineacion == 'CENTER':
            return valor_str.center(longitud, relleno)
        else:  # LEFT por defecto
            return valor_str.ljust(longitud, relleno)
    
    def generar_resumen(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Genera un resumen del archivo que se va a generar.
        
        Args:
            df: DataFrame con los datos
            
        Returns:
            Diccionario con información del resumen
        """
        campos_ordenados = self._obtener_campos_ordenados()
        
        # Calcular longitud total de línea
        longitud_total_linea = sum(campo['info']['longitud'] for campo in campos_ordenados)
        
        # Información por campo
        info_campos = []
        posicion_actual = 1
        
        for campo in campos_ordenados:
            codigo_campo = campo['codigo']
            info_campo = campo['info']
            longitud_campo = info_campo['longitud']
            
            # Valores únicos en este campo
            valores_unicos = df[codigo_campo].nunique() if codigo_campo in df.columns else 0
            
            info_campos.append({
                'codigo': codigo_campo,
                'nombre': info_campo['nombre'],
                'posicion_inicio': posicion_actual,
                'posicion_fin': posicion_actual + longitud_campo - 1,
                'longitud': longitud_campo,
                'tipo': info_campo['tipo_dato'],
                'valores_unicos': valores_unicos
            })
            
            posicion_actual += longitud_campo
        
        return {
            'dj_codigo': self.dj_codigo,
            'total_filas': len(df),
            'total_campos': len(campos_ordenados),
            'longitud_linea': longitud_total_linea,
            'extension_archivo': self.extension,
            'empresa': self.empresa.get('nombre', 'No especificada'),
            'rut_empresa': self.empresa.get('rut', 'No especificado'),
            'campos': info_campos,
            'fecha_generacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def generar_archivo_simple(df: pd.DataFrame, dj_codigo: str, empresa: Dict[str, Any], 
                          output_path: str = None, db_path: str = None) -> str:
    """
    Función de conveniencia para generar archivo de DJ simple.
    
    Args:
        df: DataFrame validado con los datos
        dj_codigo: Código de la declaración jurada
        empresa: Diccionario con datos de la empresa
        output_path: Ruta donde guardar el archivo
        db_path: Ruta opcional al archivo Access
        
    Returns:
        Ruta del archivo generado
    """
    # Obtener metadata
    metadata = obtener_metadata(dj_codigo, db_path)
    
    # Crear generador y generar archivo
    generator = GeneratorSimple(metadata, empresa)
    return generator.generar_archivo(df, output_path)


if __name__ == "__main__":
    # Ejemplo de uso
    import pandas as pd
    
    # Datos de ejemplo
    df_ejemplo = pd.DataFrame({
        'C1': ['12345678-9', '98765432-1'],
        'C2': [1000000, 2500000],
        'C3': ['EMPRESA EJEMPLO S.A.', 'OTRA EMPRESA LTDA.']
    })
    
    # Datos de empresa
    empresa_ejemplo = {
        'rut': '76123456-7',
        'nombre': 'EMPRESA DE PRUEBA S.A.',
        'giro': 'Servicios tecnológicos'
    }
    
    try:
        print("Generando archivo para DJ 1922...")
        archivo_generado = generar_archivo_simple(df_ejemplo, "1922", empresa_ejemplo)
        
        print(f"✓ Archivo generado: {archivo_generado}")
        
        # Mostrar contenido del archivo
        if Path(archivo_generado).exists():
            with open(archivo_generado, 'r', encoding='latin-1') as f:
                contenido = f.read()
            print(f"✓ Contenido del archivo:")
            print(contenido)
        else:
            print("✗ Error: El archivo no se creó correctamente")
            
    except Exception as e:
        print(f"✗ Error generando archivo: {e}")
