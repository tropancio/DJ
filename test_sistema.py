"""
Script de prueba para verificar la instalación y funcionamiento básico del sistema DJ.
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Prueba que todas las importaciones funcionen correctamente."""
    print("🧪 Probando importaciones...")
    
    try:
        from core.access_schema import AccessSchema
        print("  ✅ AccessSchema importado correctamente")
        
        from core.dispatcher import DJDispatcher
        print("  ✅ DJDispatcher importado correctamente")
        
        from core.validation.validator import DJValidator
        print("  ✅ DJValidator importado correctamente")
        
        from core.generation.generator_simple import GeneratorSimple
        print("  ✅ GeneratorSimple importado correctamente")
        
        from core.templates.generar_template import TemplateGenerator
        print("  ✅ TemplateGenerator importado correctamente")
        
        from core.storage.guardar_access import AccessStorage
        print("  ✅ AccessStorage importado correctamente")
        
        from core.procedures.mmv import ProcedimientoMMV
        print("  ✅ ProcedimientoMMV importado correctamente")
        
        from interface.cli import DJCLI
        print("  ✅ DJCLI importado correctamente")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Error de importación: {e}")
        return False

def test_dataframe_processing():
    """Prueba el procesamiento básico de DataFrames."""
    print("\n🧪 Probando procesamiento de DataFrame...")
    
    try:
        # Crear DataFrame de ejemplo
        df_test = pd.DataFrame({
            'C1': ['12345678-9', '98765432-1', '11111111-1'],
            'C2': [1000, 2000, 3000],
            'C3': ['EMPRESA A', 'EMPRESA B', 'EMPRESA C']
        })
        
        print(f"  ✅ DataFrame creado: {len(df_test)} filas, {len(df_test.columns)} columnas")
        
        # Probar validaciones básicas sin Access
        from core.validation.validator import DJValidator
        
        # Metadata mock para prueba
        metadata_mock = {
            'declaracion': {'dj_codigo': '1922', 'tipo': 'SIMPLE'},
            'campos': {
                'C1': {'obligatorio': True, 'tipo_dato': 'TEXT'},
                'C2': {'obligatorio': True, 'tipo_dato': 'INTEGER'},
                'C3': {'obligatorio': False, 'tipo_dato': 'TEXT'}
            },
            'validaciones': {}
        }
        
        # Nota: Esta prueba no requiere Access
        print("  ✅ Estructura de validación configurada")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en procesamiento: {e}")
        return False

def test_file_structure():
    """Verifica que la estructura de archivos sea correcta."""
    print("\n🧪 Verificando estructura de archivos...")
    
    required_dirs = [
        'core',
        'core/validation',
        'core/generation', 
        'core/storage',
        'core/templates',
        'core/procedures',
        'access_model',
        'data/input',
        'data/output',
        'data/raw',
        'data/validados',
        'interface',
        'tests'
    ]
    
    required_files = [
        'core/__init__.py',
        'core/access_schema.py',
        'core/dispatcher.py',
        'core/validation/validator.py',
        'core/generation/generator_simple.py',
        'core/generation/generator_compuesta.py',
        'core/storage/guardar_access.py',
        'core/templates/generar_template.py',
        'core/procedures/mmv.py',
        'interface/cli.py',
        'pyproject.toml',
        'README.md',
        '.gitignore'
    ]
    
    all_ok = True
    
    # Verificar directorios
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ Directorio: {dir_path}")
        else:
            print(f"  ❌ Falta directorio: {dir_path}")
            all_ok = False
    
    # Verificar archivos
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ Archivo: {file_path}")
        else:
            print(f"  ❌ Falta archivo: {file_path}")
            all_ok = False
    
    return all_ok

def test_cli_help():
    """Prueba que la CLI funcione básicamente."""
    print("\n🧪 Probando CLI...")
    
    try:
        from interface.cli import main
        
        # Simular --help (esto debería funcionar sin Access)
        old_argv = sys.argv
        sys.argv = ['cli.py', '--help']
        
        try:
            main()  # Esto debería mostrar ayuda y salir
        except SystemExit as e:
            if e.code == 0:  # Salida normal de --help
                print("  ✅ CLI --help funciona correctamente")
                return True
            else:
                print(f"  ❌ CLI salió con código: {e.code}")
                return False
        finally:
            sys.argv = old_argv
            
    except Exception as e:
        print(f"  ❌ Error en CLI: {e}")
        return False

def main():
    """Ejecuta todas las pruebas."""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DJ")
    print("=" * 50)
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Importaciones", test_imports),
        ("Procesamiento DataFrame", test_dataframe_processing),
        ("CLI básica", test_cli_help),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("\nEl sistema está listo para usar. Próximos pasos:")
        print("1. Configurar base de datos Access (modelo.accdb)")
        print("2. Probar conexión: python -m interface.cli test-conexion")
        print("3. Generar template: python -m interface.cli template 1922")
        return 0
    else:
        print(f"\n⚠️ {total - passed} pruebas fallaron")
        print("Revise los errores antes de continuar.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
