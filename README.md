# Sistema de Declaraciones Juradas (DJ) - SII Chile

Sistema integral para generar, validar y almacenar Declaraciones Juradas del Servicio de Impuestos Internos de Chile. La metadata y reglas de validación se almacenan en una base de datos Access (`modelo.accdb`).

## 🏗️ Arquitectura

El sistema se organiza por **función**, no por DJ específica:

```
DJ/
├── core/                           # Núcleo del sistema
│   ├── access_schema.py           # Conexión y consultas a Access
│   ├── dispatcher.py              # Orquestador principal
│   ├── validation/
│   │   └── validator.py           # Motor de validación
│   ├── generation/
│   │   ├── generator_simple.py    # Generador para DJs simples
│   │   └── generator_compuesta.py # Generador para DJs compuestas
│   ├── storage/
│   │   └── guardar_access.py      # Almacenamiento en Access
│   ├── templates/
│   │   └── generar_template.py    # Generador de plantillas Excel
│   └── procedures/
│       └── mmv.py                 # Procedimiento especial DJ 1922
├── access_model/
│   └── modelo.accdb               # Base de datos con metadata
├── data/                          # Directorio de datos
├── interface/
│   └── cli.py                     # Interfaz de línea de comandos
└── tests/                         # Pruebas unitarias
```

## 🔧 Tipos de DJ

- **SIMPLES**: Una sola tabla de datos
- **COMPUESTAS**: Múltiples secciones que se combinan en una tabla final

## 📊 Base de Datos Access

### Tablas principales:

- **DECLARACIONES**: Información básica de cada DJ
- **CAMPOS**: Definición de campos (código, tipo, longitud, etc.)
- **VALIDACIONES**: Reglas de validación con expresiones Python

### Estructura de validaciones:

```sql
VALIDACIONES:
├── CAMPO_ID          # Referencia al campo
├── DJ_CODIGO         # Código de la DJ
├── CODIGO_VALIDACION # Código único (ej: H997)
├── TIPO_VALIDACION   # obligatorio, rango, regex, lookup, condicional
├── EXPRESION_PY      # Código Python evaluable con eval()
└── MENSAJE_ERROR     # Mensaje descriptivo del error
```

## 📥 Flujo de Trabajo

### 1. Generar Template Excel
```bash
python -m interface.cli template 1922 -o template_1922.xlsx
```

El template incluye:
- **Fila 1**: Nombres descriptivos de campos
- **Fila 2**: Códigos técnicos (C1, C2, ...) - **NO MODIFICAR**
- **Comentarios**: Información detallada por campo
- **Validaciones**: Listas desplegables, rangos, etc.

### 2. Cargar Datos
Los usuarios completan el template Excel a partir de la fila 3.

### 3. Validar y Procesar
```bash
python -m interface.cli procesar 1922 datos.xlsx -e "76123456-7,MI EMPRESA S.A."
```

## 🔍 Sistema de Validación

### Expresiones Python
Las validaciones se escriben como expresiones Python que se evalúan con `eval()`:

```python
# Ejemplos de validaciones:
"len(str(valor)) <= 12"                    # Longitud máxima
"isinstance(valor, int) and valor > 0"     # Entero positivo
"valor in lookup('CODIGOS_SII', 'CODIGO', valor, 'CODIGO')"  # Tabla lookup
"not es_nulo(valor)"                       # Campo obligatorio
"entre(valor, 1, 999999)"                  # Rango numérico
```

### Contexto disponible:
- `valor`, `v`: Valor actual del campo
- `fila`: Serie pandas con toda la fila
- `df`: DataFrame completo
- Funciones: `es_nulo()`, `es_numerico()`, `longitud()`, `entre()`, `lookup()`, etc.

### Resultado de validación:
```python
{
  "valido": False,
  "errores": [
    {"fila": 5, "columna": "C2", "codigo": "H997", "error": "Valor fuera de rango"}
  ],
  "resumen": {
    "total_filas": 100,
    "errores_totales": 5,
    "columnas_con_error": ["C2"]
  },
  "validaciones_omitidas": [...]
}
```

## 📤 Generación de Archivos

Los archivos de salida son texto plano con formato específico del SII:
- **Extensión**: Últimos 3 dígitos del código DJ (ej: DJ1922 → `.922`)
- **Formato**: Una línea por registro, campos de longitud fija
- **Codificación**: `latin-1`
- **Sin encabezados**: Solo datos

## 💾 Almacenamiento

Los datos validados pueden guardarse en Access con metadata adicional:
```python
# Campos agregados automáticamente:
- DJ_CODIGO: Código de la DJ
- RUT_EMPRESA: RUT de la empresa
- FECHA_CARGA: Timestamp de carga
- USUARIO_CARGA: Usuario que cargó
- ID_REGISTRO: ID único del registro
```

## 🚀 Uso Programático

### Procesar DJ Simple
```python
from core import procesar_dj_desde_excel

empresa = {"rut": "76123456-7", "nombre": "MI EMPRESA S.A."}
resultado = procesar_dj_desde_excel("datos.xlsx", "1922", empresa)

if resultado["exito"]:
    print(f"Archivo generado: {resultado['archivos_generados']['archivo_sii']}")
```

### Procesar DJ Compuesta
```python
from core.dispatcher import DJDispatcher

dispatcher = DJDispatcher()
dataframes_secciones = {
    "SECCION_1": df_seccion1,
    "SECCION_2": df_seccion2
}

resultado = dispatcher.procesar_dj_completo("1925", empresa, dataframes_secciones)
```

### Validar únicamente
```python
from core.validation import validar_dj

resultado_validacion = validar_dj(df, "1922")
if not resultado_validacion["valido"]:
    for error in resultado_validacion["errores"]:
        print(f"Error fila {error['fila']}: {error['error']}")
```

## 🛠️ CLI - Interfaz de Línea de Comandos

### Comandos principales:

```bash
# Información de una DJ
python -m interface.cli info 1922

# Generar template
python -m interface.cli template 1922 -o plantilla.xlsx

# Validar datos
python -m interface.cli validar 1922 datos.xlsx -e "rut,nombre"

# Procesar completo
python -m interface.cli procesar 1922 datos.xlsx -e empresa.json --guardar-access

# MMV (DJ 1922) con lógica especial
python -m interface.cli mmv ventas.xlsx 202403 -e empresa.json

# Probar conexión a Access
python -m interface.cli test-conexion --verbose
```

### Formatos de empresa:
```bash
# Formato simple
-e "76123456-7,MI EMPRESA S.A."

# JSON directo
-e '{"rut":"76123456-7","nombre":"MI EMPRESA S.A.","usuario":"admin"}'

# Archivo JSON
-e empresa.json
```

## 📋 Procedimientos Especiales

### MMV (Movimiento Mensual de Ventas) - DJ 1922

Incluye transformaciones específicas:
- Conversión de formatos de fecha
- Validación de RUTs chilenos
- Cálculo automático de IVA
- Validación de consistencia entre montos
- Detección de documentos duplicados

```python
from core.procedures.mmv import procesar_mmv_desde_excel

resultado = procesar_mmv_desde_excel("ventas.xlsx", empresa, "202403")
```

## 🧪 Instalación y Configuración

### Requisitos:
```bash
pip install pandas pyodbc openpyxl python-dateutil
```

### Configuración de Access:
1. Instalar Microsoft Access Database Engine
2. Configurar ODBC para archivos `.accdb`
3. Colocar `modelo.accdb` en `access_model/`

### Estructura de `modelo.accdb`:
```sql
CREATE TABLE DECLARACIONES (
    DJ_CODIGO TEXT(10) PRIMARY KEY,
    NOMBRE TEXT(255),
    TIPO TEXT(20),  -- 'SIMPLE' o 'COMPUESTA'
    DESCRIPCION TEXT,
    ACTIVA YESNO
);

CREATE TABLE CAMPOS (
    CAMPO_ID AUTONUMBER PRIMARY KEY,
    DJ_CODIGO TEXT(10),
    CODIGO_CAMPO TEXT(10),  -- C1, C2, C3...
    NOMBRE_CAMPO TEXT(255),
    TIPO_DATO TEXT(20),     -- TEXT, INTEGER, DECIMAL, DATE
    LONGITUD INTEGER,
    DECIMALES INTEGER,
    OBLIGATORIO YESNO,
    POSICION INTEGER,
    ALINEACION TEXT(10),    -- LEFT, RIGHT, CENTER
    RELLENO TEXT(1),        -- Carácter de relleno
    FORMATO_EJEMPLO TEXT(100),
    DESCRIPCION TEXT,
    SECCION TEXT(50),       -- Para DJs compuestas
    TABLA_LOOKUP TEXT(50)   -- Tabla de referencia
);

CREATE TABLE VALIDACIONES (
    VALIDACION_ID AUTONUMBER PRIMARY KEY,
    CAMPO_ID INTEGER,
    DJ_CODIGO TEXT(10),
    CODIGO_VALIDACION TEXT(10),  -- H997, H998, etc.
    TIPO_VALIDACION TEXT(20),    -- obligatorio, rango, regex, lookup
    EXPRESION_PY TEXT,           -- Expresión Python
    MENSAJE_ERROR TEXT(255),
    ACTIVA YESNO
);
```

## 🔧 Desarrollo y Extensión

### Agregar nueva DJ:
1. Insertar registro en `DECLARACIONES`
2. Definir campos en `CAMPOS`
3. Configurar validaciones en `VALIDACIONES`
4. Probar con `python -m interface.cli info CODIGO_DJ`

### Agregar procedimiento especial:
1. Crear archivo en `core/procedures/`
2. Heredar de clase base o seguir patrón MMV
3. Registrar en CLI si es necesario

### Agregar nueva validación:
1. Implementar función en contexto de `validator.py`
2. Documentar en `EXPRESION_PY`
3. Probar con datos de ejemplo

## 📈 Monitoreo y Logs

El sistema genera logs detallados durante el procesamiento:
- Tiempo de ejecución por paso
- Estadísticas de validación
- Errores y advertencias
- Archivos generados

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Pull Request

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para detalles.

## 📞 Soporte

Para soporte técnico o consultas sobre el sistema:
- Email: your.email@example.com
- Issues: GitHub Issues del proyecto

---

**Desarrollado para el procesamiento eficiente de Declaraciones Juradas del SII Chile** 🇨🇱
