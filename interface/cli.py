"""
Interfaz de línea de comandos para el sistema de Declaraciones Juradas.
Proporciona comandos para generar templates, validar, procesar y generar DJs.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd

# Importar módulos del core
sys.path.append(str(Path(__file__).parent.parent))

from core.dispatcher import DJDispatcher, procesar_dj_desde_excel, procesar_dj_desde_dataframe
from core.access_schema import AccessSchema
from core.procedures.mmv import ProcedimientoMMV, procesar_mmv_desde_excel


class DJCLI:
    """Interfaz de línea de comandos para el sistema DJ."""
    
    def __init__(self):
        self.dispatcher = None
        self.db_path = None
    
    def setup_dispatcher(self, db_path: str = None):
        """Configura el dispatcher con la ruta de BD especificada."""
        self.db_path = db_path
        self.dispatcher = DJDispatcher(db_path)
    
    def cmd_info(self, args):
        """Comando: Mostrar información de una DJ."""
        try:
            self.setup_dispatcher(args.db_path)
            info = self.dispatcher.obtener_info_dj(args.dj_codigo)
            
            print(f"\n{'='*60}")
            print(f"INFORMACIÓN DJ {args.dj_codigo}")
            print(f"{'='*60}")
            print(f"Nombre: {info['declaracion']['nombre']}")
            print(f"Tipo: {info['declaracion']['tipo']}")
            print(f"Estado: {'ACTIVA' if info['declaracion']['activa'] else 'INACTIVA'}")
            print(f"Descripción: {info['declaracion']['descripcion']}")
            
            print(f"\nRESUMEN:")
            print(f"• Total de campos: {info['resumen']['total_campos']}")
            print(f"• Campos obligatorios: {info['resumen']['campos_obligatorios']}")
            print(f"• Total de validaciones: {info['resumen']['total_validaciones']}")
            
            if info['declaracion']['tipo'] == 'COMPUESTA':
                print(f"• Secciones: {', '.join(info['resumen']['secciones'])}")
                
                for seccion, campos in info['campos_por_seccion'].items():
                    print(f"\nSECCIÓN: {seccion}")
                    for campo in campos:
                        obligatorio = "⚠️" if campo['obligatorio'] else ""
                        print(f"  • {campo['codigo']}: {campo['nombre']} ({campo['tipo']}) {obligatorio}")
            else:
                print(f"\nCAMPOS:")
                # Para DJ simple, mostrar campos desde metadata
                metadata = self.dispatcher._cargar_metadata(args.dj_codigo)
                for codigo, info_campo in metadata['campos'].items():
                    obligatorio = "⚠️" if info_campo['obligatorio'] else ""
                    print(f"  • {codigo}: {info_campo['nombre']} ({info_campo['tipo_dato']}) {obligatorio}")
            
            if args.verbose:
                print(f"\nVALIDACIONES POR CAMPO:")
                for campo, validaciones in info['validaciones_por_campo'].items():
                    print(f"  {campo}:")
                    for val in validaciones:
                        print(f"    • {val['codigo']}: {val['mensaje']}")
            
        except Exception as e:
            print(f"❌ Error obteniendo información: {e}")
            return 1
        
        return 0
    
    def cmd_template(self, args):
        """Comando: Generar template Excel."""
        try:
            self.setup_dispatcher(args.db_path)
            
            print(f"Generando template para DJ {args.dj_codigo}...")
            archivo_template = self.dispatcher.generar_template(args.dj_codigo, args.output)
            
            print(f"✅ Template generado: {archivo_template}")
            
            # Mostrar información adicional si se solicita
            if args.verbose:
                info = self.dispatcher.obtener_info_dj(args.dj_codigo)
                print(f"📋 Tipo de DJ: {info['declaracion']['tipo']}")
                print(f"📋 Total de campos: {info['resumen']['total_campos']}")
                if info['declaracion']['tipo'] == 'COMPUESTA':
                    print(f"📋 Secciones: {', '.join(info['resumen']['secciones'])}")
            
        except Exception as e:
            print(f"❌ Error generando template: {e}")
            return 1
        
        return 0
    
    def cmd_validar(self, args):
        """Comando: Validar datos sin generar archivo."""
        try:
            self.setup_dispatcher(args.db_path)
            
            print(f"Cargando datos desde {args.input}...")
            
            # Cargar empresa
            empresa = self._cargar_empresa(args.empresa)
            
            # Procesar solo validación
            opciones = {
                'generar_reporte_errores': True,
                'guardar_access': False,  # Solo validar
                'forzar_generacion': False
            }
            
            resultado = procesar_dj_desde_excel(args.input, args.dj_codigo, empresa, opciones, args.db_path)
            
            # Mostrar resultados
            validacion = resultado.get('validacion', {})
            
            if validacion.get('valido', False):
                print("✅ DATOS VÁLIDOS")
                resumen = validacion.get('resumen', {})
                print(f"📊 Total de filas: {resumen.get('total_filas', 0)}")
            else:
                print("❌ DATOS CON ERRORES")
                resumen = validacion.get('resumen', {})
                print(f"📊 Total de filas: {resumen.get('total_filas', 0)}")
                print(f"📊 Errores encontrados: {resumen.get('errores_totales', 0)}")
                print(f"📊 Columnas con error: {len(resumen.get('columnas_con_error', []))}")
                
                # Mostrar primeros errores
                errores = validacion.get('errores', [])
                print(f"\nPRIMEROS ERRORES:")
                for i, error in enumerate(errores[:5]):
                    fila = error.get('fila', 'N/A')
                    columna = error.get('columna', 'N/A')
                    mensaje = error.get('error', 'N/A')
                    print(f"  {i+1}. Fila {fila}, Campo {columna}: {mensaje}")
                
                if len(errores) > 5:
                    print(f"  ... y {len(errores) - 5} errores más")
                
                # Buscar archivo de reporte de errores
                archivos_generados = resultado.get('archivos_generados', {})
                if 'reporte_errores' in archivos_generados:
                    print(f"\n📄 Reporte detallado: {archivos_generados['reporte_errores']}")
            
        except Exception as e:
            print(f"❌ Error en validación: {e}")
            return 1
        
        return 0 if validacion.get('valido', False) else 1
    
    def cmd_procesar(self, args):
        """Comando: Procesar DJ completa (validar + generar)."""
        try:
            self.setup_dispatcher(args.db_path)
            
            print(f"Procesando DJ {args.dj_codigo} desde {args.input}...")
            
            # Cargar empresa
            empresa = self._cargar_empresa(args.empresa)
            
            # Configurar opciones
            opciones = {
                'generar_reporte_errores': True,
                'guardar_access': args.guardar_access,
                'forzar_generacion': args.forzar,
                'ruta_archivo_salida': args.output
            }
            
            resultado = procesar_dj_desde_excel(args.input, args.dj_codigo, empresa, opciones, args.db_path)
            
            # Mostrar resultados
            if resultado['exito']:
                print("✅ PROCESAMIENTO EXITOSO")
                print(f"🔄 Pasos completados: {', '.join(resultado['pasos_completados'])}")
                
                archivos = resultado.get('archivos_generados', {})
                if 'archivo_sii' in archivos:
                    print(f"📄 Archivo SII generado: {archivos['archivo_sii']}")
                
                if args.verbose:
                    validacion = resultado.get('validacion', {})
                    resumen = validacion.get('resumen', {})
                    print(f"📊 Filas procesadas: {resumen.get('total_filas', 0)}")
                    
                    if 'storage' in resultado:
                        storage = resultado['storage']
                        print(f"💾 Filas guardadas en Access: {storage.get('filas_insertadas', 0)}")
            else:
                print("❌ PROCESAMIENTO CON ERRORES")
                for error in resultado.get('errores', []):
                    print(f"  • {error}")
                
                # Mostrar errores de validación si existen
                validacion = resultado.get('validacion', {})
                if not validacion.get('valido', True):
                    errores = validacion.get('errores', [])
                    print(f"\n📋 Errores de validación ({len(errores)}):")
                    for i, error in enumerate(errores[:3]):
                        fila = error.get('fila', 'N/A')
                        columna = error.get('columna', 'N/A')
                        mensaje = error.get('error', 'N/A')
                        print(f"  {i+1}. Fila {fila}, Campo {columna}: {mensaje}")
                    
                    if len(errores) > 3:
                        print(f"  ... y {len(errores) - 3} errores más")
            
        except Exception as e:
            print(f"❌ Error en procesamiento: {e}")
            return 1
        
        return 0 if resultado['exito'] else 1
    
    def cmd_mmv(self, args):
        """Comando: Procesar MMV (DJ 1922) con lógica especial."""
        try:
            print(f"Procesando MMV período {args.periodo} desde {args.input}...")
            
            # Cargar empresa
            empresa = self._cargar_empresa(args.empresa)
            
            # Configurar opciones
            opciones = {
                'generar_reporte_errores': True,
                'guardar_access': args.guardar_access,
                'forzar_generacion': args.forzar,
                'ruta_archivo_salida': args.output
            }
            
            resultado = procesar_mmv_desde_excel(args.input, empresa, args.periodo, opciones, args.db_path)
            
            # Mostrar resultados
            if resultado['exito']:
                print("✅ MMV PROCESADO EXITOSAMENTE")
                print(f"📅 Período: {resultado['periodo']}")
                print(f"📊 Filas procesadas: {resultado.get('filas_procesadas', 0)}")
                print(f"🔄 Pasos MMV: {', '.join(resultado['pasos_mmv'])}")
                
                resultado_general = resultado.get('resultado_general', {})
                archivos = resultado_general.get('archivos_generados', {})
                if 'archivo_sii' in archivos:
                    print(f"📄 Archivo SII generado: {archivos['archivo_sii']}")
            else:
                print("❌ ERROR EN PROCESAMIENTO MMV")
                for error in resultado.get('errores_mmv', []):
                    print(f"  • {error}")
            
        except Exception as e:
            print(f"❌ Error en MMV: {e}")
            return 1
        
        return 0 if resultado['exito'] else 1
    
    def cmd_test_conexion(self, args):
        """Comando: Probar conexión a Access."""
        try:
            print("Probando conexión a Access...")
            schema = AccessSchema(args.db_path)
            
            if schema.test_connection():
                print("✅ Conexión exitosa")
                
                # Obtener estadísticas básicas si se solicita
                if args.verbose:
                    try:
                        with schema._get_connection() as conn:
                            cursor = conn.cursor()
                            
                            # Contar declaraciones
                            cursor.execute("SELECT COUNT(*) FROM DECLARACIONES")
                            total_djs = cursor.fetchone()[0]
                            print(f"📊 Total DJs configuradas: {total_djs}")
                            
                            # Contar campos
                            cursor.execute("SELECT COUNT(*) FROM CAMPOS")
                            total_campos = cursor.fetchone()[0]
                            print(f"📊 Total campos definidos: {total_campos}")
                            
                            # Contar validaciones
                            cursor.execute("SELECT COUNT(*) FROM VALIDACIONES WHERE ACTIVA = True")
                            total_validaciones = cursor.fetchone()[0]
                            print(f"📊 Total validaciones activas: {total_validaciones}")
                            
                    except Exception as e:
                        print(f"⚠️ Error obteniendo estadísticas: {e}")
                
                return 0
            else:
                print("❌ Error de conexión")
                return 1
                
        except Exception as e:
            print(f"❌ Error probando conexión: {e}")
            return 1
    
    def _cargar_empresa(self, empresa_input: str) -> Dict[str, Any]:
        """Carga datos de empresa desde JSON o parámetros."""
        
        # Si es una ruta a archivo JSON
        if empresa_input.endswith('.json'):
            try:
                with open(empresa_input, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                raise ValueError(f"Error cargando empresa desde JSON: {e}")
        
        # Si es JSON directo
        try:
            return json.loads(empresa_input)
        except json.JSONDecodeError:
            # Si no es JSON, asumir formato simple "RUT,NOMBRE"
            partes = empresa_input.split(',')
            if len(partes) >= 2:
                return {
                    'rut': partes[0].strip(),
                    'nombre': partes[1].strip(),
                    'usuario': 'CLI'
                }
            else:
                raise ValueError("Formato de empresa inválido. Use: RUT,NOMBRE o JSON")


def main():
    """Función principal de la CLI."""
    
    parser = argparse.ArgumentParser(
        description="Sistema de Declaraciones Juradas del SII",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

# Generar template para DJ 1922
python cli.py template 1922 -o template_1922.xlsx

# Validar datos
python cli.py validar 1922 datos.xlsx -e "76123456-7,MI EMPRESA S.A."

# Procesar DJ completa
python cli.py procesar 1922 datos.xlsx -e empresa.json -o salida.922

# Procesar MMV
python cli.py mmv datos_ventas.xlsx 202403 -e empresa.json

# Probar conexión
python cli.py test-conexion
        """
    )
    
    parser.add_argument('--db-path', help='Ruta al archivo Access (modelo.accdb)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Salida detallada')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando info
    parser_info = subparsers.add_parser('info', help='Mostrar información de una DJ')
    parser_info.add_argument('dj_codigo', help='Código de la DJ (ej: 1922)')
    
    # Comando template
    parser_template = subparsers.add_parser('template', help='Generar template Excel')
    parser_template.add_argument('dj_codigo', help='Código de la DJ')
    parser_template.add_argument('-o', '--output', help='Archivo de salida')
    
    # Comando validar
    parser_validar = subparsers.add_parser('validar', help='Validar datos')
    parser_validar.add_argument('dj_codigo', help='Código de la DJ')
    parser_validar.add_argument('input', help='Archivo Excel con datos')
    parser_validar.add_argument('-e', '--empresa', required=True, 
                               help='Datos empresa (JSON, archivo.json, o "RUT,NOMBRE")')
    
    # Comando procesar
    parser_procesar = subparsers.add_parser('procesar', help='Procesar DJ completa')
    parser_procesar.add_argument('dj_codigo', help='Código de la DJ')
    parser_procesar.add_argument('input', help='Archivo Excel con datos')
    parser_procesar.add_argument('-e', '--empresa', required=True,
                                help='Datos empresa (JSON, archivo.json, o "RUT,NOMBRE")')
    parser_procesar.add_argument('-o', '--output', help='Archivo de salida')
    parser_procesar.add_argument('--guardar-access', action='store_true',
                                help='Guardar datos en Access')
    parser_procesar.add_argument('--forzar', action='store_true',
                                help='Forzar generación aunque haya errores')
    
    # Comando MMV
    parser_mmv = subparsers.add_parser('mmv', help='Procesar MMV (DJ 1922)')
    parser_mmv.add_argument('input', help='Archivo Excel con datos de ventas')
    parser_mmv.add_argument('periodo', help='Período YYYYMM (ej: 202403)')
    parser_mmv.add_argument('-e', '--empresa', required=True,
                           help='Datos empresa (JSON, archivo.json, o "RUT,NOMBRE")')
    parser_mmv.add_argument('-o', '--output', help='Archivo de salida')
    parser_mmv.add_argument('--guardar-access', action='store_true',
                           help='Guardar datos en Access')
    parser_mmv.add_argument('--forzar', action='store_true',
                           help='Forzar generación aunque haya errores')
    
    # Comando test-conexion
    parser_test = subparsers.add_parser('test-conexion', help='Probar conexión a Access')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Crear instancia CLI y ejecutar comando
    cli = DJCLI()
    
    try:
        if args.command == 'info':
            return cli.cmd_info(args)
        elif args.command == 'template':
            return cli.cmd_template(args)
        elif args.command == 'validar':
            return cli.cmd_validar(args)
        elif args.command == 'procesar':
            return cli.cmd_procesar(args)
        elif args.command == 'mmv':
            return cli.cmd_mmv(args)
        elif args.command == 'test-conexion':
            return cli.cmd_test_conexion(args)
        else:
            print(f"❌ Comando desconocido: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Operación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
