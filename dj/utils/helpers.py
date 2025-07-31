"""
Helpers - Funciones auxiliares para la librería DJ.

Contiene funciones de utilidad para formateo, validación
y manipulación de datos comunes en documentos tributarios.
"""

import re
from typing import Optional, Union
from decimal import Decimal, ROUND_HALF_UP


def clean_rut(rut: str) -> str:
    """
    Limpia un RUT eliminando puntos, guiones y espacios.
    
    Args:
        rut: RUT a limpiar
        
    Returns:
        str: RUT limpio
    """
    if not isinstance(rut, str):
        return str(rut)
    
    return re.sub(r'[.\-\s]', '', rut).upper()


def format_rut(rut: str) -> str:
    """
    Formatea un RUT con el formato estándar (12.345.678-9).
    
    Args:
        rut: RUT a formatear
        
    Returns:
        str: RUT formateado
    """
    rut_limpio = clean_rut(rut)
    
    if len(rut_limpio) < 2:
        return rut
    
    # Separar número y dígito verificador
    numero = rut_limpio[:-1]
    dv = rut_limpio[-1]
    
    # Formatear número con puntos
    numero_formateado = ""
    for i, digito in enumerate(reversed(numero)):
        if i > 0 and i % 3 == 0:
            numero_formateado = "." + numero_formateado
        numero_formateado = digito + numero_formateado
    
    return f"{numero_formateado}-{dv}"


def validate_rut_digit(rut: str) -> bool:
    """
    Valida el dígito verificador de un RUT chileno.
    
    Args:
        rut: RUT a validar
        
    Returns:
        bool: True si el dígito verificador es correcto
    """
    rut_limpio = clean_rut(rut)
    
    if len(rut_limpio) < 2:
        return False
    
    # Separar número y dígito verificador
    numero = rut_limpio[:-1]
    dv_proporcionado = rut_limpio[-1]
    
    # Validar que el número sea numérico
    if not numero.isdigit():
        return False
    
    # Calcular dígito verificador
    suma = 0
    multiplicador = 2
    
    for digito in reversed(numero):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = str(11 - resto) if resto != 0 else '0'
    if dv_calculado == '10':
        dv_calculado = 'K'
    
    return dv_proporcionado == dv_calculado


def calculate_rut_digit(rut_numero: str) -> str:
    """
    Calcula el dígito verificador de un RUT.
    
    Args:
        rut_numero: Número del RUT sin dígito verificador
        
    Returns:
        str: Dígito verificador calculado
    """
    if not rut_numero.isdigit():
        raise ValueError("El número del RUT debe ser numérico")
    
    suma = 0
    multiplicador = 2
    
    for digito in reversed(rut_numero):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv = str(11 - resto) if resto != 0 else '0'
    if dv == '10':
        dv = 'K'
    
    return dv


def format_amount(amount: Union[int, float, Decimal, str], decimales: int = 0) -> str:
    """
    Formatea un monto con separadores de miles y decimales.
    
    Args:
        amount: Monto a formatear
        decimales: Número de decimales a mostrar
        
    Returns:
        str: Monto formateado
    """
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            return str(amount)
    
    if isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    
    # Redondear al número de decimales especificado
    if decimales > 0:
        factor = Decimal('10') ** decimales
        amount = (amount * factor).quantize(Decimal('1'), rounding=ROUND_HALF_UP) / factor
    else:
        amount = amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    # Formatear con separadores de miles
    if decimales > 0:
        formato = f"{{:,.{decimales}f}}"
    else:
        formato = "{:,.0f}"
    
    return formato.format(float(amount)).replace(',', '.')  # Usar punto como separador de miles


def format_amount_clp(amount: Union[int, float, Decimal, str]) -> str:
    """
    Formatea un monto en pesos chilenos.
    
    Args:
        amount: Monto a formatear
        
    Returns:
        str: Monto formateado con símbolo de peso
    """
    monto_formateado = format_amount(amount, 0)
    return f"$ {monto_formateado}"


def clean_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Limpia un texto eliminando caracteres especiales no permitidos.
    
    Args:
        text: Texto a limpiar
        max_length: Longitud máxima opcional
        
    Returns:
        str: Texto limpio
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Eliminar caracteres de control y espacios extras
    text = re.sub(r'\s+', ' ', text)  # Múltiples espacios a uno solo
    text = re.sub(r'[^\w\s\-\.\(\)\/&]', '', text)  # Solo caracteres permitidos
    text = text.strip()
    
    # Truncar si se especifica longitud máxima
    if max_length and len(text) > max_length:
        text = text[:max_length].strip()
    
    return text


def validate_email(email: str) -> bool:
    """
    Valida el formato de un email.
    
    Args:
        email: Email a validar
        
    Returns:
        bool: True si el formato es válido
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))


def normalize_text(text: str) -> str:
    """
    Normaliza un texto eliminando tildes y caracteres especiales.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Mapeo de caracteres con tilde a sin tilde
    tildes = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
    }
    
    for con_tilde, sin_tilde in tildes.items():
        text = text.replace(con_tilde, sin_tilde)
    
    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        str: Texto truncado
    """
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    # Calcular espacio disponible para el texto
    espacio_disponible = max_length - len(suffix)
    if espacio_disponible <= 0:
        return suffix[:max_length]
    
    return text[:espacio_disponible] + suffix


def generate_folio_reference(tipo_documento: str, folio: Union[int, str]) -> str:
    """
    Genera una referencia de folio formateada.
    
    Args:
        tipo_documento: Código del tipo de documento
        folio: Número de folio
        
    Returns:
        str: Referencia formateada
    """
    return f"{tipo_documento}-{str(folio).zfill(8)}"


def parse_amount(amount_str: str) -> Optional[float]:
    """
    Convierte una cadena de texto a un monto numérico.
    
    Args:
        amount_str: Cadena que representa un monto
        
    Returns:
        float: Monto convertido o None si no es válido
    """
    if not isinstance(amount_str, str):
        try:
            return float(amount_str)
        except (ValueError, TypeError):
            return None
    
    # Limpiar la cadena
    amount_clean = re.sub(r'[^\d\.\-]', '', amount_str)
    
    try:
        return float(amount_clean)
    except ValueError:
        return None


def validate_positive_amount(amount: Union[int, float, str]) -> bool:
    """
    Valida que un monto sea positivo.
    
    Args:
        amount: Monto a validar
        
    Returns:
        bool: True si es positivo
    """
    try:
        if isinstance(amount, str):
            amount = parse_amount(amount)
            if amount is None:
                return False
        
        return float(amount) >= 0
    except (ValueError, TypeError):
        return False


def get_document_type_name(tipo_documento: str) -> str:
    """
    Obtiene el nombre legible de un tipo de documento.
    
    Args:
        tipo_documento: Código del tipo de documento
        
    Returns:
        str: Nombre del tipo de documento
    """
    tipos = {
        '33': 'Factura Electrónica',
        '34': 'Factura No Afecta o Exenta Electrónica',
        '39': 'Boleta Electrónica', 
        '41': 'Boleta No Afecta o Exenta Electrónica',
        '46': 'Factura de Compra Electrónica',
        '52': 'Guía de Despacho Electrónica',
        '56': 'Nota de Débito Electrónica',
        '61': 'Nota de Crédito Electrónica',
        '110': 'Factura de Exportación Electrónica',
        '111': 'Nota de Débito de Exportación Electrónica',
        '112': 'Nota de Crédito de Exportación Electrónica'
    }
    
    return tipos.get(str(tipo_documento), f'Documento Tipo {tipo_documento}')


def format_date_for_xml(date_obj) -> str:
    """
    Formatea una fecha para uso en XML (formato ISO).
    
    Args:
        date_obj: Objeto fecha, string o timestamp
        
    Returns:
        str: Fecha en formato YYYY-MM-DD
    """
    from datetime import datetime, date
    
    if isinstance(date_obj, str):
        return date_obj  # Asumir que ya está en formato correcto
    elif isinstance(date_obj, date):
        return date_obj.strftime('%Y-%m-%d')
    elif isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d')
    else:
        # Intentar convertir timestamp
        try:
            dt = datetime.fromtimestamp(float(date_obj))
            return dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return datetime.now().strftime('%Y-%m-%d')


def sanitize_xml_text(text: str) -> str:
    """
    Sanitiza texto para uso seguro en XML.
    
    Args:
        text: Texto a sanitizar
        
    Returns:
        str: Texto sanitizado
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Reemplazar caracteres especiales XML
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&apos;'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text
