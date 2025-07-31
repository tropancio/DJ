# DJ - Librería de Documentos Tributarios

## Descripción
DJ es una librería Python para el manejo de documentos tributarios chilenos, incluyendo almacenamiento, validación y generación de documentos DTE (Documento Tributario Electrónico).

## Funcionalidades

### 1. Almacenamiento de DJ
- **DataGenerar**: Manejo de datos para generación de documentos
- **DataDeclaracion**: Gestión de datos de declaraciones
- **DataSii**: Integración con datos del SII (Servicio de Impuestos Internos)

### 2. Validación de DJ
- Validación de estructura XML
- Verificación de datos obligatorios
- Validación de formato de campos

### 3. Generación de DJ
- Generación de XML de documentos tributarios
- Aplicación de firmas digitales
- Formateo según estándares SII

### 4. Módulo de Datos Estandarizados
- Códigos de documentos tributarios
- Tipos de documentos
- Validaciones estándar
- Configuraciones del SII

## Instalación

```bash
pip install dj
```

## Uso Básico

```python
from dj import DJ
from dj.storage import DataGenerar, DataDeclaracion, DataSii
from dj.validator import DJValidator
from dj.generator import DJGenerator

# Crear instancia principal
dj = DJ()

# Almacenar datos
data_gen = DataGenerar()
data_gen.store(documento_data)

# Validar documento
validator = DJValidator()
is_valid, errors = validator.validate(documento)

# Generar documento
generator = DJGenerator()
xml_doc = generator.generate(data)
```

## Estructura del Proyecto

```
dj/
├── __init__.py
├── storage/
│   ├── __init__.py
│   ├── data_generar.py
│   ├── data_declaracion.py
│   └── data_sii.py
├── validator/
│   ├── __init__.py
│   └── dj_validator.py
├── generator/
│   ├── __init__.py
│   └── dj_generator.py
├── data/
│   ├── __init__.py
│   ├── standards.py
│   └── sii_codes.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

## Contribución
Las contribuciones son bienvenidas. Por favor, crea un issue antes de enviar un pull request.

## Licencia
MIT License
