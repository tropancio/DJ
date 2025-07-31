"""
Procedimiento especial para DJ 1922 - Movimiento Mensual de Ventas (MMV).
Implementa lógica específica para el procesamiento de esta declaración.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import math
from ..dispatcher import DJDispatcher


class ProcedimientoMMV:
    """Procedimiento especial para DJ 1922 (Movimiento Mensual de Ventas)."""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa el procedimiento MMV.
        
        Args:
            db_path: Ruta opcional al archivo Access
        """
        self.dispatcher = DJDispatcher(db_path)
        self.dj_codigo = "1922"
    
    def procesar_mmv(self, datos_ventas: pd.DataFrame, empresa: Dict[str, Any],
                    periodo: str, opciones: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa el Movimiento Mensual de Ventas con lógica específica.
        
        Args:
            datos_ventas: DataFrame con datos de ventas del período
            empresa: Datos de la empresa
            periodo: Período en formato YYYYMM (ej: "202403")
            opciones: Opciones de procesamiento
            
        Returns:
            Resultado del procesamiento
        """
        if opciones is None:
            opciones = {}
        
        resultado = {
            "dj_codigo": self.dj_codigo,
            "periodo": periodo,
            "empresa": empresa,
            "inicio_proceso": datetime.now(),
            "pasos_mmv": [],
            "errores_mmv": [],
            "exito": False
        }
        
        try:
            # 1. Validar período
            print(f"Validando período {periodo}...")
            self._validar_periodo(periodo)
            resultado["pasos_mmv"].append("periodo_validado")
            
            # 2. Procesar y transformar datos de ventas
            print("Procesando datos de ventas...")
            df_transformado = self._transformar_datos_ventas(datos_ventas, periodo, empresa)
            resultado["filas_procesadas"] = len(df_transformado)
            resultado["pasos_mmv"].append("datos_transformados")
            
            # 3. Aplicar validaciones específicas de MMV
            print("Aplicando validaciones específicas MMV...")
            errores_mmv = self._validar_mmv_especifico(df_transformado, periodo)
            if errores_mmv:
                resultado["errores_mmv"].extend(errores_mmv)
            resultado["pasos_mmv"].append("validaciones_mmv")
            
            # 4. Procesar con dispatcher general
            print("Procesando con sistema general...")
            opciones_dispatcher = {
                **opciones,
                "validaciones_adicionales": errores_mmv,
                "procedimiento_especial": "MMV"
            }
            
            resultado_dispatcher = self.dispatcher.procesar_dj_completo(
                self.dj_codigo, empresa, df_transformado, opciones_dispatcher
            )
            
            # 5. Combinar resultados
            resultado.update({
                "resultado_general": resultado_dispatcher,
                "exito": resultado_dispatcher["exito"] and len(resultado["errores_mmv"]) == 0
            })
            
        except Exception as e:
            resultado["errores_mmv"].append(f"Error en procedimiento MMV: {str(e)}")
        
        finally:
            resultado["fin_proceso"] = datetime.now()
            resultado["duracion_total"] = (
                resultado["fin_proceso"] - resultado["inicio_proceso"]
            ).total_seconds()
        
        return resultado
    
    def _validar_periodo(self, periodo: str) -> None:
        """Valida que el período tenga formato correcto YYYYMM."""
        if not periodo or len(periodo) != 6:
            raise ValueError("Período debe tener formato YYYYMM")
        
        try:
            año = int(periodo[:4])
            mes = int(periodo[4:6])
            
            if año < 2000 or año > 2100:
                raise ValueError("Año debe estar entre 2000 y 2100")
            
            if mes < 1 or mes > 12:
                raise ValueError("Mes debe estar entre 01 y 12")
                
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Período debe contener solo números")
            raise
    
    def _transformar_datos_ventas(self, datos_ventas: pd.DataFrame, periodo: str, 
                                 empresa: Dict[str, Any]) -> pd.DataFrame:
        """
        Transforma datos de ventas al formato requerido por DJ 1922.
        
        Args:
            datos_ventas: DataFrame con datos originales de ventas
            periodo: Período YYYYMM
            empresa: Datos de la empresa
            
        Returns:
            DataFrame transformado según estructura DJ 1922
        """
        # Crear DataFrame base con estructura DJ 1922
        df_mmv = pd.DataFrame()
        
        # Mapeo de campos de ventas a campos DJ 1922
        # (Estos mapeos deberían venir de configuración o metadata)
        mapeo_campos = {
            'fecha_documento': 'C1',  # Fecha del documento
            'tipo_documento': 'C2',   # Tipo de documento
            'numero_documento': 'C3', # Número de documento
            'rut_cliente': 'C4',      # RUT del cliente
            'nombre_cliente': 'C5',   # Nombre del cliente
            'monto_neto': 'C6',       # Monto neto
            'monto_iva': 'C7',        # Monto IVA
            'monto_total': 'C8'       # Monto total
        }
        
        # Aplicar mapeo básico
        for campo_origen, campo_destino in mapeo_campos.items():
            if campo_origen in datos_ventas.columns:
                df_mmv[campo_destino] = datos_ventas[campo_origen]
            else:
                # Campo faltante, llenar con valores por defecto
                df_mmv[campo_destino] = self._obtener_valor_defecto(campo_destino)
        
        # Transformaciones específicas
        df_mmv = self._aplicar_transformaciones_mmv(df_mmv, periodo, empresa)
        
        return df_mmv
    
    def _obtener_valor_defecto(self, campo_codigo: str) -> Any:
        """Obtiene valor por defecto para un campo según su tipo."""
        # Esta lógica podría venir de la metadata
        valores_defecto = {
            'C1': datetime.now().date(),
            'C2': 33,  # Factura electrónica por defecto
            'C3': 0,
            'C4': '',
            'C5': '',
            'C6': 0,
            'C7': 0,
            'C8': 0
        }
        
        return valores_defecto.get(campo_codigo, '')
    
    def _aplicar_transformaciones_mmv(self, df: pd.DataFrame, periodo: str, 
                                     empresa: Dict[str, Any]) -> pd.DataFrame:
        """Aplica transformaciones específicas para MMV."""
        
        # 1. Formatear fechas
        if 'C1' in df.columns:
            df['C1'] = pd.to_datetime(df['C1']).dt.strftime('%Y%m%d')
        
        # 2. Validar y formatear RUTs
        if 'C4' in df.columns:
            df['C4'] = df['C4'].apply(self._formatear_rut)
        
        # 3. Calcular montos si faltan
        if 'C6' in df.columns and 'C7' in df.columns and 'C8' in df.columns:
            # Si falta monto total, calcularlo
            mask_total_faltante = (df['C8'] == 0) | df['C8'].isna()
            df.loc[mask_total_faltante, 'C8'] = (
                df.loc[mask_total_faltante, 'C6'] + df.loc[mask_total_faltante, 'C7']
            )
            
            # Si falta IVA, calcularlo (19%)
            mask_iva_faltante = (df['C7'] == 0) | df['C7'].isna()
            df.loc[mask_iva_faltante, 'C7'] = (
                df.loc[mask_iva_faltante, 'C6'] * 0.19
            ).round(0)
        
        # 4. Agregar campos adicionales de control
        df['_PERIODO'] = periodo
        df['_RUT_EMPRESA'] = empresa.get('rut', '')
        df['_FECHA_PROCESO'] = datetime.now().strftime('%Y%m%d')
        
        return df
    
    def _formatear_rut(self, rut: str) -> str:
        """Formatea un RUT al estándar chileno."""
        if pd.isna(rut) or not rut:
            return ''
        
        # Limpiar RUT
        rut_limpio = str(rut).upper().replace('.', '').replace('-', '').strip()
        
        # Validar formato básico
        if len(rut_limpio) < 2:
            return rut_limpio
        
        # Separar número y dígito verificador
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
        
        # Formatear con guión
        return f"{numero}-{dv}"
    
    def _validar_mmv_especifico(self, df: pd.DataFrame, periodo: str) -> List[str]:
        """Aplica validaciones específicas del MMV."""
        errores = []
        
        # 1. Validar que no haya documentos duplicados
        if 'C2' in df.columns and 'C3' in df.columns:
            duplicados = df.groupby(['C2', 'C3']).size()
            docs_duplicados = duplicados[duplicados > 1]
            if len(docs_duplicados) > 0:
                errores.append(f"Se encontraron {len(docs_duplicados)} documentos duplicados")
        
        # 2. Validar rangos de montos
        if 'C6' in df.columns:  # Monto neto
            montos_negativos = df[df['C6'] < 0]
            if len(montos_negativos) > 0:
                errores.append(f"Se encontraron {len(montos_negativos)} documentos con monto neto negativo")
        
        # 3. Validar coherencia IVA
        if 'C6' in df.columns and 'C7' in df.columns:
            # Tolerancia del 1% para diferencias de redondeo
            iva_esperado = (df['C6'] * 0.19).round(0)
            diferencia = abs(df['C7'] - iva_esperado)
            tolerancia = df['C6'] * 0.01  # 1% de tolerancia
            
            iva_inconsistente = diferencia > tolerancia
            if iva_inconsistente.sum() > 0:
                errores.append(f"Se encontraron {iva_inconsistente.sum()} documentos con IVA inconsistente")
        
        # 4. Validar fechas del período
        if 'C1' in df.columns:
            año_periodo = int(periodo[:4])
            mes_periodo = int(periodo[4:6])
            
            # Convertir fechas para validación
            fechas_doc = pd.to_datetime(df['C1'], format='%Y%m%d', errors='coerce')
            
            # Documentos fuera del período
            fuera_periodo = (
                (fechas_doc.dt.year != año_periodo) | 
                (fechas_doc.dt.month != mes_periodo)
            )
            
            if fuera_periodo.sum() > 0:
                errores.append(f"Se encontraron {fuera_periodo.sum()} documentos fuera del período {periodo}")
        
        return errores
    
    def generar_resumen_mmv(self, df: pd.DataFrame, periodo: str) -> Dict[str, Any]:
        """Genera resumen específico del MMV."""
        
        resumen = {
            "periodo": periodo,
            "total_documentos": len(df),
            "fecha_generacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Resumen por tipo de documento
        if 'C2' in df.columns:
            resumen["por_tipo_documento"] = df['C2'].value_counts().to_dict()
        
        # Resumen de montos
        if 'C6' in df.columns and 'C7' in df.columns and 'C8' in df.columns:
            resumen["montos"] = {
                "total_neto": float(df['C6'].sum()),
                "total_iva": float(df['C7'].sum()),
                "total_bruto": float(df['C8'].sum()),
                "promedio_documento": float(df['C8'].mean()),
                "documento_mayor": float(df['C8'].max()),
                "documento_menor": float(df['C8'].min())
            }
        
        # Top 10 clientes por monto
        if 'C5' in df.columns and 'C8' in df.columns:
            top_clientes = df.groupby('C5')['C8'].sum().nlargest(10)
            resumen["top_10_clientes"] = top_clientes.to_dict()
        
        return resumen


def procesar_mmv_desde_excel(ruta_excel: str, empresa: Dict[str, Any], periodo: str,
                           opciones: Dict[str, Any] = None, db_path: str = None) -> Dict[str, Any]:
    """
    Función de conveniencia para procesar MMV desde Excel.
    
    Args:
        ruta_excel: Ruta al archivo Excel con datos de ventas
        empresa: Datos de la empresa
        periodo: Período en formato YYYYMM
        opciones: Opciones de procesamiento
        db_path: Ruta opcional al archivo Access
        
    Returns:
        Resultado del procesamiento MMV
    """
    # Cargar datos de ventas
    datos_ventas = pd.read_excel(ruta_excel)
    
    # Procesar con MMV
    mmv = ProcedimientoMMV(db_path)
    return mmv.procesar_mmv(datos_ventas, empresa, periodo, opciones)


if __name__ == "__main__":
    # Ejemplo de uso
    import pandas as pd
    
    # Datos de ejemplo de ventas
    datos_ventas_ejemplo = pd.DataFrame({
        'fecha_documento': ['2024-03-01', '2024-03-02', '2024-03-03'],
        'tipo_documento': [33, 33, 34],  # 33=Factura, 34=Factura exenta
        'numero_documento': [1001, 1002, 1003],
        'rut_cliente': ['12345678-9', '98765432-1', '11111111-1'],
        'nombre_cliente': ['CLIENTE A', 'CLIENTE B', 'CLIENTE C'],
        'monto_neto': [100000, 200000, 150000],
        'monto_iva': [19000, 38000, 0],  # Factura exenta sin IVA
        'monto_total': [119000, 238000, 150000]
    })
    
    # Datos de empresa
    empresa_ejemplo = {
        'rut': '76123456-7',
        'nombre': 'EMPRESA DE PRUEBA S.A.',
        'usuario': 'admin'
    }
    
    try:
        print("Procesando MMV (DJ 1922)...")
        mmv = ProcedimientoMMV()
        resultado = mmv.procesar_mmv(datos_ventas_ejemplo, empresa_ejemplo, "202403")
        
        if resultado["exito"]:
            print("✓ MMV procesado exitosamente")
            print(f"  - Período: {resultado['periodo']}")
            print(f"  - Filas procesadas: {resultado['filas_procesadas']}")
            print(f"  - Pasos MMV: {', '.join(resultado['pasos_mmv'])}")
        else:
            print("✗ Error en procesamiento MMV:")
            for error in resultado["errores_mmv"]:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"✗ Error: {e}")
