"""
Ejemplo básico de uso de la librería DJ.

Este ejemplo muestra cómo usar las funcionalidades principales
de la librería para almacenar, validar y generar documentos tributarios.
"""

from dj import DJ
from datetime import date

def ejemplo_factura_electronica():
    """Ejemplo de manejo de factura electrónica."""
    print("=== Ejemplo: Factura Electrónica ===")
    
    # Crear instancia de DJ
    dj = DJ()
    dj.info()
    
    # Datos de la factura
    factura_data = {
        'tipo_documento': '33',
        'folio': 12345,
        'fecha_emision': date(2024, 1, 15),
        'rut_emisor': '12345678-5',
        'razon_social_emisor': 'Empresa Ejemplo SPA',
        'rut_receptor': '87654321-6',
        'razon_social_receptor': 'Cliente Ejemplo LTDA',
        'monto_neto': 84034,
        'monto_iva': 15966,
        'monto_total': 100000,
        'detalle': [
            {
                'nombre': 'Servicio de Consultoría',
                'cantidad': 1,
                'precio': 84034,
                'monto': 84034
            }
        ]
    }
    
    print(f"\n1. Almacenando documento...")
    # Almacenar en DataGenerar
    doc_id = dj.storage['generar'].store(factura_data)
    print(f"   Documento almacenado con ID: {doc_id}")
    
    print(f"\n2. Validando documento...")
    # Validar documento
    es_valido, errores = dj.validator.validate(factura_data)
    print(f"   Válido: {es_valido}")
    if errores:
        print("   Errores encontrados:")
        for error in errores:
            print(f"   - {error.campo}: {error.mensaje}")
    
    print(f"\n3. Generando XML...")
    # Generar XML
    try:
        xml_documento = dj.generator.generate(factura_data)
        print(f"   XML generado exitosamente ({len(xml_documento)} caracteres)")
        print(f"   Primeros 200 caracteres:")
        print(f"   {xml_documento[:200]}...")
    except Exception as e:
        print(f"   Error generando XML: {e}")
    
    print(f"\n4. Consultando datos del SII...")
    # Validar RUT
    validacion_rut = dj.storage['sii'].validar_rut(factura_data['rut_emisor'])
    print(f"   RUT emisor válido: {validacion_rut['valido']}")
    
    # Obtener info del tipo de documento
    tipo_doc = dj.storage['sii'].get_tipo_documento('33')
    if tipo_doc:
        print(f"   Tipo documento: {tipo_doc['nombre']}")
    
    return doc_id


def ejemplo_boleta_electronica():
    """Ejemplo de manejo de boleta electrónica."""
    print("\n\n=== Ejemplo: Boleta Electrónica ===")
    
    dj = DJ()
    
    # Datos de la boleta
    boleta_data = {
        'tipo_documento': '39',
        'folio': 67890,
        'fecha_emision': date(2024, 1, 16),
        'rut_emisor': '12345678-5',
        'razon_social_emisor': 'Comercial Ejemplo SPA',
        'monto_total': 25000
    }
    
    print(f"\n1. Almacenando boleta...")
    doc_id = dj.storage['generar'].store(boleta_data)
    print(f"   Boleta almacenada con ID: {doc_id}")
    
    print(f"\n2. Validando boleta...")
    es_valido, errores = dj.validator.validate(boleta_data)
    print(f"   Válida: {es_valido}")
    
    print(f"\n3. Verificando reglas de negocio...")
    # Verificar si el monto es válido para boleta
    monto_valido, mensaje_error = dj.standards.validar_monto_documento('39', 25000)
    print(f"   Monto válido: {monto_valido}")
    if mensaje_error:
        print(f"   Error: {mensaje_error}")
    
    print(f"\n4. Generando XML...")
    try:
        xml_boleta = dj.generator.generate(boleta_data)
        print(f"   XML generado exitosamente ({len(xml_boleta)} caracteres)")
    except Exception as e:
        print(f"   Error generando XML: {e}")
    
    return doc_id


def ejemplo_declaracion():
    """Ejemplo de manejo de declaración."""
    print("\n\n=== Ejemplo: Declaración Tributaria ===")
    
    dj = DJ()
    
    # Datos de la declaración
    declaracion_data = {
        'folio': 'F29-2024-001',
        'periodo': '202401',
        'tipo_declaracion': 'F29',
        'rut_declarante': '12345678-5',
        'fecha_declaracion': date(2024, 2, 20),
        'monto_total': 1500000,
        'datos_declaracion': {
            'ventas_netas': 10000000,
            'debito_fiscal': 1900000,
            'credito_fiscal': 400000,
            'iva_a_pagar': 1500000
        }
    }
    
    print(f"\n1. Almacenando declaración...")
    folio = dj.storage['declaracion'].store(declaracion_data)
    print(f"   Declaración almacenada con folio: {folio}")
    
    print(f"\n2. Consultando declaración...")
    declaracion = dj.storage['declaracion'].get(folio)
    if declaracion:
        print(f"   Período: {declaracion.periodo}")
        print(f"   Monto total: ${declaracion.monto_total:,.0f}")
        print(f"   Estado: {declaracion.estado.value}")
    
    print(f"\n3. Estadísticas de declaraciones...")
    stats = dj.storage['declaracion'].get_estadisticas()
    print(f"   Total declaraciones: {stats['total_declaraciones']}")
    print(f"   Monto total declarado: ${stats['monto_total']:,.0f}")
    
    return folio


def ejemplo_consultas_sii():
    """Ejemplo de consultas y códigos del SII."""
    print("\n\n=== Ejemplo: Consultas SII ===")
    
    dj = DJ()
    
    print(f"\n1. Códigos de documentos soportados:")
    tipos_doc = dj.sii_codes.listar_tipos_documento()
    for codigo, info in list(tipos_doc.items())[:5]:  # Mostrar solo los primeros 5
        print(f"   {codigo}: {info.nombre}")
    
    print(f"\n2. Búsqueda de actividades económicas:")
    actividades = dj.sii_codes.buscar_actividad_por_nombre("informática")
    for actividad in actividades:
        print(f"   {actividad.codigo}: {actividad.descripcion}")
    
    print(f"\n3. Comunas de Santiago:")
    comunas_santiago = dj.sii_codes.buscar_comuna_por_nombre("santiago")
    for comuna in comunas_santiago[:3]:  # Mostrar solo las primeras 3
        print(f"   {comuna.codigo}: {comuna.nombre}")
    
    print(f"\n4. Validación de RUT:")
    ruts_test = ['12345678-5', '87654321-6', '12345678-0']
    for rut in ruts_test:
        validacion = dj.storage['sii'].validar_rut(rut)
        print(f"   {rut}: {'Válido' if validacion['valido'] else 'Inválido'}")


def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("Librería DJ - Ejemplos de Uso")
    print("=" * 40)
    
    try:
        # Ejecutar ejemplos
        ejemplo_factura_electronica()
        ejemplo_boleta_electronica()
        ejemplo_declaracion()
        ejemplo_consultas_sii()
        
        print("\n\n=== Resumen Final ===")
        
        # Crear instancia para resumen
        dj = DJ()
        
        # Mostrar contadores
        print(f"Documentos almacenados: {dj.storage['generar'].count()}")
        print(f"Declaraciones almacenadas: {dj.storage['declaracion'].count()}")
        print(f"Consultas SII realizadas: {dj.storage['sii'].count()}")
        
        print(f"\nTipos de documento soportados: {len(dj.sii_codes.listar_tipos_documento())}")
        print(f"Actividades económicas disponibles: {len(dj.sii_codes.listar_actividades_economicas())}")
        print(f"Comunas disponibles: {len(dj.sii_codes.listar_comunas())}")
        
        print(f"\n¡Ejemplos ejecutados exitosamente!")
        
    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
