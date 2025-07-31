"""
SiiCodes - Módulo de códigos del SII.

Contiene todos los códigos oficiales del Servicio de Impuestos Internos
utilizados en documentos tributarios.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class CodigoSii:
    """Estructura para códigos SII."""
    codigo: str
    nombre: str
    descripcion: str
    activo: bool = True


class TipoTabla(Enum):
    """Tipos de tablas SII disponibles."""
    TIPOS_DOCUMENTO = "tipos_documento"
    ACTIVIDADES_ECONOMICAS = "actividades_economicas"
    COMUNAS = "comunas"
    REGIONES = "regiones"
    PAISES = "paises"
    MONEDAS = "monedas"
    UNIDADES_MEDIDA = "unidades_medida"
    TIPOS_REFERENCIA = "tipos_referencia"
    INDICADORES_SERVICIO = "indicadores_servicio"


class SiiCodes:
    """
    Clase que contiene todos los códigos oficiales del SII.
    
    Proporciona acceso a las tablas de códigos utilizadas
    en documentos tributarios electrónicos.
    """
    
    def __init__(self):
        """Inicializa las tablas de códigos del SII."""
        self._tipos_documento = self._init_tipos_documento()
        self._actividades_economicas = self._init_actividades_economicas()
        self._comunas = self._init_comunas()
        self._regiones = self._init_regiones()
        self._paises = self._init_paises()
        self._monedas = self._init_monedas()
        self._unidades_medida = self._init_unidades_medida()
        self._tipos_referencia = self._init_tipos_referencia()
        self._indicadores_servicio = self._init_indicadores_servicio()
    
    def _init_tipos_documento(self) -> Dict[str, CodigoSii]:
        """Inicializa los tipos de documento tributario."""
        return {
            '29': CodigoSii('29', 'Zarpe', 'Zarpe'),
            '30': CodigoSii('30', 'Factura', 'Factura'),
            '32': CodigoSii('32', 'Factura de Venta Bienes y Servicios No Afectos o Exentos de IVA', 'Factura Exenta'),
            '33': CodigoSii('33', 'Factura Electrónica', 'Factura Electrónica'),
            '34': CodigoSii('34', 'Factura No Afecta o Exenta Electrónica', 'Factura Exenta Electrónica'),
            '35': CodigoSii('35', 'Boleta', 'Boleta'),
            '38': CodigoSii('38', 'Boleta Exenta', 'Boleta Exenta'),
            '39': CodigoSii('39', 'Boleta Electrónica', 'Boleta Electrónica'),
            '41': CodigoSii('41', 'Boleta No Afecta o Exenta Electrónica', 'Boleta Exenta Electrónica'),
            '43': CodigoSii('43', 'Liquidación-Factura', 'Liquidación-Factura'),
            '46': CodigoSii('46', 'Factura de Compra', 'Factura de Compra'),
            '50': CodigoSii('50', 'Guía de Despacho', 'Guía de Despacho'),
            '52': CodigoSii('52', 'Guía de Despacho Electrónica', 'Guía de Despacho Electrónica'),
            '55': CodigoSii('55', 'Nota de Débito', 'Nota de Débito'),
            '56': CodigoSii('56', 'Nota de Débito Electrónica', 'Nota de Débito Electrónica'),
            '60': CodigoSii('60', 'Nota de Crédito', 'Nota de Crédito'),
            '61': CodigoSii('61', 'Nota de Crédito Electrónica', 'Nota de Crédito Electrónica'),
            '103': CodigoSii('103', 'Liquidación', 'Liquidación'),
            '110': CodigoSii('110', 'Factura de Exportación Electrónica', 'Factura de Exportación'),
            '111': CodigoSii('111', 'Nota de Débito de Exportación Electrónica', 'Nota de Débito de Exportación'),
            '112': CodigoSii('112', 'Nota de Crédito de Exportación Electrónica', 'Nota de Crédito de Exportación')
        }
    
    def _init_actividades_economicas(self) -> Dict[str, CodigoSii]:
        """Inicializa las actividades económicas más comunes."""
        return {
            '620200': CodigoSii('620200', 'Consultores en programas de informática', 'Servicios de consultoría en software'),
            '620100': CodigoSii('620100', 'Programación informática', 'Desarrollo de software'),
            '620300': CodigoSii('620300', 'Gestión de recursos informáticos', 'Administración de sistemas'),
            '631100': CodigoSii('631100', 'Procesamiento de datos', 'Procesamiento y hosting de datos'),
            '620900': CodigoSii('620900', 'Otras actividades de informática', 'Otras actividades relacionadas con informática'),
            '691000': CodigoSii('691000', 'Actividades jurídicas', 'Servicios legales'),
            '692000': CodigoSii('692000', 'Actividades de contabilidad', 'Servicios contables'),
            '702000': CodigoSii('702000', 'Actividades de consultoría de gestión', 'Consultoría empresarial'),
            '711000': CodigoSii('711000', 'Actividades de arquitectura e ingeniería', 'Servicios de arquitectura e ingeniería'),
            '749000': CodigoSii('749000', 'Otras actividades profesionales', 'Otras actividades profesionales'),
            '471100': CodigoSii('471100', 'Comercio al por menor en almacenes no especializados', 'Retail general'),
            '561000': CodigoSii('561000', 'Restaurantes y servicios móviles de comidas', 'Servicios de comida'),
            '681000': CodigoSii('681000', 'Actividades inmobiliarias', 'Servicios inmobiliarios'),
            '851000': CodigoSii('851000', 'Enseñanza pre-escolar y primaria', 'Educación básica'),
            '862100': CodigoSii('862100', 'Actividades de médicos generales', 'Servicios médicos generales')
        }
    
    def _init_comunas(self) -> Dict[str, CodigoSii]:
        """Inicializa las comunas chilenas más importantes."""
        return {
            '13101': CodigoSii('13101', 'Santiago', 'Comuna de Santiago, Región Metropolitana'),
            '13102': CodigoSii('13102', 'Cerrillos', 'Comuna de Cerrillos, Región Metropolitana'),
            '13103': CodigoSii('13103', 'Cerro Navia', 'Comuna de Cerro Navia, Región Metropolitana'),
            '13104': CodigoSii('13104', 'Conchalí', 'Comuna de Conchalí, Región Metropolitana'),
            '13105': CodigoSii('13105', 'El Bosque', 'Comuna de El Bosque, Región Metropolitana'),
            '13106': CodigoSii('13106', 'Estación Central', 'Comuna de Estación Central, Región Metropolitana'),
            '13107': CodigoSii('13107', 'Huechuraba', 'Comuna de Huechuraba, Región Metropolitana'),
            '13108': CodigoSii('13108', 'Independencia', 'Comuna de Independencia, Región Metropolitana'),
            '13109': CodigoSii('13109', 'La Cisterna', 'Comuna de La Cisterna, Región Metropolitana'),
            '13110': CodigoSii('13110', 'La Florida', 'Comuna de La Florida, Región Metropolitana'),
            '13111': CodigoSii('13111', 'La Granja', 'Comuna de La Granja, Región Metropolitana'),
            '13112': CodigoSii('13112', 'La Pintana', 'Comuna de La Pintana, Región Metropolitana'),
            '13113': CodigoSii('13113', 'La Reina', 'Comuna de La Reina, Región Metropolitana'),
            '13114': CodigoSii('13114', 'Las Condes', 'Comuna de Las Condes, Región Metropolitana'),
            '13115': CodigoSii('13115', 'Lo Barnechea', 'Comuna de Lo Barnechea, Región Metropolitana'),
            '13116': CodigoSii('13116', 'Lo Espejo', 'Comuna de Lo Espejo, Región Metropolitana'),
            '13117': CodigoSii('13117', 'Lo Prado', 'Comuna de Lo Prado, Región Metropolitana'),
            '13118': CodigoSii('13118', 'Macul', 'Comuna de Macul, Región Metropolitana'),
            '13119': CodigoSii('13119', 'Maipú', 'Comuna de Maipú, Región Metropolitana'),
            '13120': CodigoSii('13120', 'Ñuñoa', 'Comuna de Ñuñoa, Región Metropolitana'),
            '13121': CodigoSii('13121', 'Pedro Aguirre Cerda', 'Comuna de Pedro Aguirre Cerda, Región Metropolitana'),
            '13122': CodigoSii('13122', 'Peñalolén', 'Comuna de Peñalolén, Región Metropolitana'),
            '13123': CodigoSii('13123', 'Providencia', 'Comuna de Providencia, Región Metropolitana'),
            '13124': CodigoSii('13124', 'Pudahuel', 'Comuna de Pudahuel, Región Metropolitana'),
            '13125': CodigoSii('13125', 'Quilicura', 'Comuna de Quilicura, Región Metropolitana'),
            '13126': CodigoSii('13126', 'Quinta Normal', 'Comuna de Quinta Normal, Región Metropolitana'),
            '13127': CodigoSii('13127', 'Recoleta', 'Comuna de Recoleta, Región Metropolitana'),
            '13128': CodigoSii('13128', 'Renca', 'Comuna de Renca, Región Metropolitana'),
            '13129': CodigoSii('13129', 'San Joaquín', 'Comuna de San Joaquín, Región Metropolitana'),
            '13130': CodigoSii('13130', 'San Miguel', 'Comuna de San Miguel, Región Metropolitana'),
            '13131': CodigoSii('13131', 'San Ramón', 'Comuna de San Ramón, Región Metropolitana'),
            '13132': CodigoSii('13132', 'Vitacura', 'Comuna de Vitacura, Región Metropolitana'),
            '5101': CodigoSii('5101', 'Valparaíso', 'Comuna de Valparaíso, Región de Valparaíso'),
            '5109': CodigoSii('5109', 'Viña del Mar', 'Comuna de Viña del Mar, Región de Valparaíso'),
            '8101': CodigoSii('8101', 'Concepción', 'Comuna de Concepción, Región del Biobío'),
            '10101': CodigoSii('10101', 'Puerto Montt', 'Comuna de Puerto Montt, Región de Los Lagos'),
            '1101': CodigoSii('1101', 'Iquique', 'Comuna de Iquique, Región de Tarapacá'),
            '2101': CodigoSii('2101', 'Antofagasta', 'Comuna de Antofagasta, Región de Antofagasta'),
            '3101': CodigoSii('3101', 'Copiapó', 'Comuna de Copiapó, Región de Atacama'),
            '4101': CodigoSii('4101', 'La Serena', 'Comuna de La Serena, Región de Coquimbo'),
            '6101': CodigoSii('6101', 'Rancagua', 'Comuna de Rancagua, Región del Libertador'),
            '7101': CodigoSii('7101', 'Talca', 'Comuna de Talca, Región del Maule'),
            '9101': CodigoSii('9101', 'Temuco', 'Comuna de Temuco, Región de La Araucanía'),
            '14101': CodigoSii('14101', 'Valdivia', 'Comuna de Valdivia, Región de Los Ríos'),
            '11101': CodigoSii('11101', 'Coyhaique', 'Comuna de Coyhaique, Región de Aysén'),
            '12101': CodigoSii('12101', 'Punta Arenas', 'Comuna de Punta Arenas, Región de Magallanes')
        }
    
    def _init_regiones(self) -> Dict[str, CodigoSii]:
        """Inicializa las regiones de Chile."""
        return {
            '15': CodigoSii('15', 'Arica y Parinacota', 'Región de Arica y Parinacota'),
            '1': CodigoSii('1', 'Tarapacá', 'Región de Tarapacá'),
            '2': CodigoSii('2', 'Antofagasta', 'Región de Antofagasta'),
            '3': CodigoSii('3', 'Atacama', 'Región de Atacama'),
            '4': CodigoSii('4', 'Coquimbo', 'Región de Coquimbo'),
            '5': CodigoSii('5', 'Valparaíso', 'Región de Valparaíso'),
            '13': CodigoSii('13', 'Metropolitana', 'Región Metropolitana de Santiago'),
            '6': CodigoSii('6', 'O\'Higgins', 'Región del Libertador General Bernardo O\'Higgins'),
            '7': CodigoSii('7', 'Maule', 'Región del Maule'),
            '16': CodigoSii('16', 'Ñuble', 'Región de Ñuble'),
            '8': CodigoSii('8', 'Biobío', 'Región del Biobío'),
            '9': CodigoSii('9', 'Araucanía', 'Región de La Araucanía'),
            '14': CodigoSii('14', 'Los Ríos', 'Región de Los Ríos'),
            '10': CodigoSii('10', 'Los Lagos', 'Región de Los Lagos'),
            '11': CodigoSii('11', 'Aysén', 'Región Aysén del General Carlos Ibáñez del Campo'),
            '12': CodigoSii('12', 'Magallanes', 'Región de Magallanes y de la Antártica Chilena')
        }
    
    def _init_paises(self) -> Dict[str, CodigoSii]:
        """Inicializa los códigos de países."""
        return {
            '152': CodigoSii('152', 'Chile', 'República de Chile'),
            '213': CodigoSii('213', 'Argentina', 'República Argentina'),
            '076': CodigoSii('076', 'Brasil', 'República Federativa del Brasil'),
            '170': CodigoSii('170', 'Colombia', 'República de Colombia'),
            '218': CodigoSii('218', 'Ecuador', 'República del Ecuador'),
            '600': CodigoSii('600', 'Paraguay', 'República del Paraguay'),
            '604': CodigoSii('604', 'Perú', 'República del Perú'),
            '858': CodigoSii('858', 'Uruguay', 'República Oriental del Uruguay'),
            '862': CodigoSii('862', 'Venezuela', 'República Bolivariana de Venezuela'),
            '840': CodigoSii('840', 'Estados Unidos', 'Estados Unidos de América'),
            '124': CodigoSii('124', 'Canadá', 'Canadá'),
            '484': CodigoSii('484', 'México', 'Estados Unidos Mexicanos'),
            '724': CodigoSii('724', 'España', 'Reino de España'),
            '250': CodigoSii('250', 'Francia', 'República Francesa'),
            '276': CodigoSii('276', 'Alemania', 'República Federal de Alemania'),
            '380': CodigoSii('380', 'Italia', 'República Italiana'),
            '826': CodigoSii('826', 'Reino Unido', 'Reino Unido de Gran Bretaña e Irlanda del Norte'),
            '392': CodigoSii('392', 'Japón', 'Japón'),
            '156': CodigoSii('156', 'China', 'República Popular China'),
            '036': CodigoSii('036', 'Australia', 'Mancomunidad de Australia')
        }
    
    def _init_monedas(self) -> Dict[str, CodigoSii]:
        """Inicializa los códigos de monedas."""
        return {
            'CLP': CodigoSii('CLP', 'Peso Chileno', 'Peso Chileno'),
            'USD': CodigoSii('USD', 'Dólar Estadounidense', 'Dólar de los Estados Unidos de América'),
            'EUR': CodigoSii('EUR', 'Euro', 'Euro'),
            'CLF': CodigoSii('CLF', 'Unidad de Fomento', 'Unidad de Fomento (Chile)'),
            'UTM': CodigoSii('UTM', 'Unidad Tributaria Mensual', 'Unidad Tributaria Mensual (Chile)'),
            'ARS': CodigoSii('ARS', 'Peso Argentino', 'Peso Argentino'),
            'BRL': CodigoSii('BRL', 'Real Brasileño', 'Real Brasileño'),
            'GBP': CodigoSii('GBP', 'Libra Esterlina', 'Libra Esterlina'),
            'JPY': CodigoSii('JPY', 'Yen Japonés', 'Yen Japonés'),
            'CNY': CodigoSii('CNY', 'Yuan Chino', 'Renminbi Chino')
        }
    
    def _init_unidades_medida(self) -> Dict[str, CodigoSii]:
        """Inicializa las unidades de medida."""
        return {
            'UN': CodigoSii('UN', 'Unidad', 'Unidad'),
            'KG': CodigoSii('KG', 'Kilogramo', 'Kilogramo'),
            'LT': CodigoSii('LT', 'Litro', 'Litro'),
            'MT': CodigoSii('MT', 'Metro', 'Metro'),
            'M2': CodigoSii('M2', 'Metro Cuadrado', 'Metro Cuadrado'),
            'M3': CodigoSii('M3', 'Metro Cúbico', 'Metro Cúbico'),
            'HR': CodigoSii('HR', 'Hora', 'Hora'),
            'DI': CodigoSii('DI', 'Día', 'Día'),
            'SE': CodigoSii('SE', 'Segundo', 'Segundo'),
            'MI': CodigoSii('MI', 'Minuto', 'Minuto'),
            'PC': CodigoSii('PC', 'Pieza', 'Pieza'),
            'PA': CodigoSii('PA', 'Par', 'Par'),
            'DO': CodigoSii('DO', 'Docena', 'Docena'),
            'CE': CodigoSii('CE', 'Centena', 'Centena'),
            'MI': CodigoSii('MI', 'Millar', 'Millar')
        }
    
    def _init_tipos_referencia(self) -> Dict[str, CodigoSii]:
        """Inicializa los tipos de referencia para notas de crédito/débito."""
        return {
            '1': CodigoSii('1', 'Anula Documento de Referencia', 'Anula documento de referencia'),
            '2': CodigoSii('2', 'Corrige Texto Documento Referencia', 'Corrige texto documento referencia'),
            '3': CodigoSii('3', 'Corrige Montos', 'Corrige montos')
        }
    
    def _init_indicadores_servicio(self) -> Dict[str, CodigoSii]:
        """Inicializa los indicadores de servicio."""
        return {
            '1': CodigoSii('1', 'Factura de Servicios Periódicos', 'Servicios periódicos'),
            '2': CodigoSii('2', 'Factura de Servicios Periódicos Domiciliarios', 'Servicios periódicos domiciliarios'),
            '3': CodigoSii('3', 'Factura de Boleta de Terceros', 'Boleta de terceros'),
            '4': CodigoSii('4', 'Factura de Servicios de Hotelería', 'Servicios de hotelería'),
            '5': CodigoSii('5', 'Factura de Servicios de Transporte Terrestre Internacional', 'Transporte terrestre internacional')
        }
    
    def get_tipo_documento(self, codigo: str) -> Optional[CodigoSii]:
        """
        Obtiene información de un tipo de documento.
        
        Args:
            codigo: Código del tipo de documento
            
        Returns:
            CodigoSii o None si no existe
        """
        return self._tipos_documento.get(str(codigo))
    
    def get_actividad_economica(self, codigo: str) -> Optional[CodigoSii]:
        """
        Obtiene información de una actividad económica.
        
        Args:
            codigo: Código de la actividad económica
            
        Returns:
            CodigoSii o None si no existe
        """
        return self._actividades_economicas.get(str(codigo))
    
    def get_comuna(self, codigo: str) -> Optional[CodigoSii]:
        """
        Obtiene información de una comuna.
        
        Args:
            codigo: Código de la comuna
            
        Returns:
            CodigoSii o None si no existe
        """
        return self._comunas.get(str(codigo))
    
    def get_region(self, codigo: str) -> Optional[CodigoSii]:
        """
        Obtiene información de una región.
        
        Args:
            codigo: Código de la región
            
        Returns:
            CodigoSii o None si no existe
        """
        return self._regiones.get(str(codigo))
    
    def get_pais(self, codigo: str) -> Optional[CodigoSii]:
        """
        Obtiene información de un país.
        
        Args:
            codigo: Código del país
            
        Returns:
            CodigoSii o None si no existe
        """
        return self._paises.get(str(codigo))
    
    def get_moneda(self, codigo: str) -> Optional[CodigoSii]:
        """
        Obtiene información de una moneda.
        
        Args:
            codigo: Código de la moneda
            
        Returns:
            CodigoSii o None si no existe
        """
        return self._monedas.get(str(codigo).upper())
    
    def get_unidad_medida(self, codigo: str) -> Optional[CodigoSii]:
        """
        Obtiene información de una unidad de medida.
        
        Args:
            codigo: Código de la unidad de medida
            
        Returns:
            CodigoSii o None si no existe
        """
        return self._unidades_medida.get(str(codigo).upper())
    
    def listar_tipos_documento(self) -> Dict[str, CodigoSii]:
        """
        Lista todos los tipos de documento disponibles.
        
        Returns:
            Dict con todos los tipos de documento
        """
        return self._tipos_documento.copy()
    
    def listar_actividades_economicas(self) -> Dict[str, CodigoSii]:
        """
        Lista todas las actividades económicas disponibles.
        
        Returns:
            Dict con todas las actividades económicas
        """
        return self._actividades_economicas.copy()
    
    def listar_comunas(self) -> Dict[str, CodigoSii]:
        """
        Lista todas las comunas disponibles.
        
        Returns:
            Dict con todas las comunas
        """
        return self._comunas.copy()
    
    def listar_regiones(self) -> Dict[str, CodigoSii]:
        """
        Lista todas las regiones disponibles.
        
        Returns:
            Dict con todas las regiones
        """
        return self._regiones.copy()
    
    def listar_monedas(self) -> Dict[str, CodigoSii]:
        """
        Lista todas las monedas disponibles.
        
        Returns:
            Dict con todas las monedas
        """
        return self._monedas.copy()
    
    def buscar_actividad_por_nombre(self, nombre_parcial: str) -> List[CodigoSii]:
        """
        Busca actividades económicas por nombre parcial.
        
        Args:
            nombre_parcial: Parte del nombre a buscar
            
        Returns:
            Lista de actividades que coinciden
        """
        nombre_lower = nombre_parcial.lower()
        resultados = []
        
        for actividad in self._actividades_economicas.values():
            if (nombre_lower in actividad.nombre.lower() or 
                nombre_lower in actividad.descripcion.lower()):
                resultados.append(actividad)
        
        return resultados
    
    def buscar_comuna_por_nombre(self, nombre_parcial: str) -> List[CodigoSii]:
        """
        Busca comunas por nombre parcial.
        
        Args:
            nombre_parcial: Parte del nombre a buscar
            
        Returns:
            Lista de comunas que coinciden
        """
        nombre_lower = nombre_parcial.lower()
        resultados = []
        
        for comuna in self._comunas.values():
            if nombre_lower in comuna.nombre.lower():
                resultados.append(comuna)
        
        return resultados
    
    def es_documento_electronico(self, codigo: str) -> bool:
        """
        Verifica si un tipo de documento es electrónico.
        
        Args:
            codigo: Código del tipo de documento
            
        Returns:
            bool: True si es documento electrónico
        """
        documentos_electronicos = [
            '33', '34', '39', '41', '46', '52', '56', '61',
            '110', '111', '112'
        ]
        return str(codigo) in documentos_electronicos
    
    def get_tabla(self, tipo_tabla: TipoTabla) -> Dict[str, CodigoSii]:
        """
        Obtiene una tabla completa de códigos.
        
        Args:
            tipo_tabla: Tipo de tabla a obtener
            
        Returns:
            Dict con todos los códigos de la tabla
        """
        tablas = {
            TipoTabla.TIPOS_DOCUMENTO: self._tipos_documento,
            TipoTabla.ACTIVIDADES_ECONOMICAS: self._actividades_economicas,
            TipoTabla.COMUNAS: self._comunas,
            TipoTabla.REGIONES: self._regiones,
            TipoTabla.PAISES: self._paises,
            TipoTabla.MONEDAS: self._monedas,
            TipoTabla.UNIDADES_MEDIDA: self._unidades_medida,
            TipoTabla.TIPOS_REFERENCIA: self._tipos_referencia,
            TipoTabla.INDICADORES_SERVICIO: self._indicadores_servicio
        }
        
        return tablas.get(tipo_tabla, {}).copy()
    
    def validar_codigo(self, codigo: str, tipo_tabla: TipoTabla) -> bool:
        """
        Valida si un código existe en una tabla específica.
        
        Args:
            codigo: Código a validar
            tipo_tabla: Tipo de tabla donde buscar
            
        Returns:
            bool: True si el código existe
        """
        tabla = self.get_tabla(tipo_tabla)
        return str(codigo) in tabla
