from pydantic import BaseModel, Field
import json

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.structured_output import ProviderStrategy

import base64

class GeneralInvoiceInformation(BaseModel):
    poliza: str|None = Field(default=None, description="Para localizar el número de póliza en documentos de Chubb de autos, busca en la parte superior del documento, normalmente en el encabezado, donde aparecen varios identificadores (número de cotización, póliza, endoso, etc.). Suele estar acompañado de etiquetas como “PÓLIZA”, “No. de póliza”, “Núm. de Póliza” o similar. El valor suele ser un código alfanumérico relativamente corto (por ejemplo, 8–15 caracteres) sin espacios, a veces con prefijos de letras seguido de números. Visualmente, puede estar destacado en negritas o con tipografía más grande y puede ubicarse cerca del logo de la aseguradora o en un bloque que resume los datos principales del contrato (póliza, vigencia, contratante). Asegúrate de diferenciarlo de otros números como el número de cliente, número de cotización o número de endoso que suelen estar en el mismo bloque pero con etiquetas distintas.")
    inicioPeriodoVigencia: str|None = Field(default=None, description="Identifica la sección donde se indica la vigencia de la póliza, normalmente titulada “Vigencia”, “Periodo de Vigencia”, “Desde / Hasta”, “Inicio de Vigencia” o similar. Suelen aparecer dos fechas: la fecha de inicio y la de término. La fecha de inicio es la que está asociada a términos como “Desde”, “Inicio”, “Fecha de inicio de vigencia” o aparece primero en un formato de rango (por ejemplo, “Del [fecha inicio] al [fecha fin]”). El formato puede ser día/mes/año (dd/mm/aaaa) o textual (por ejemplo, “06 de julio de 2022”) y en algunos documentos internos o digitalizados puede verse en formato ISO con hora y zona horaria. La ubicación típica es cerca de los datos principales de la póliza (número de póliza, contratante, producto) en las primeras secciones del documento, a veces dentro de un cuadro de resumen. Distingue este dato de otras fechas como fecha de emisión o fecha de impresión, que también suelen aparecer en encabezados pero con etiquetas claras (“Fecha de emisión”, “Fecha de expedición”).")
    finalPeriodoVigencia: str|None = Field(default=None, description="Se encuentra en la misma sección donde se detalla la vigencia de la póliza. Busca un rango de fechas que indique la cobertura del seguro, con etiquetas como “Hasta”, “Fin de vigencia”, “Vence”, “Vigente hasta” o similar. Esta fecha es generalmente la segunda en un formato de rango (“Del [inicio] al [fin]”) o viene explícitamente marcada como fecha de término. El formato suele ser el mismo que el de inicio (dd/mm/aaaa, texto completo o formato ISO con hora). Usualmente se indica que la vigencia termina a las 12:00 o a una hora fija del día especificado; si aparece la hora, se incluye junto con la fecha. Se localiza en el mismo bloque de cabecera donde están número de póliza, nombre del asegurado y otros datos del contrato. No confundir con fechas de pago, fechas de emisión o fechas de accidente, que aparecen en otras secciones enfocadas en primas o siniestros.")
    aseguradora: str|None = Field(default=None, description="La aseguradora se identifica por el nombre corporativo y el logotipo en el encabezado del documento. En documentos de Chubb, el logotipo suele ser muy visible en la parte superior (izquierda, derecha o centrado) y el nombre “CHUBB” aparece en mayúsculas, en ocasiones acompañado de la razón social completa (por ejemplo, “Chubb Seguros México, S.A.”). Además del logotipo, el nombre puede aparecer en el pie de página, en textos legales o en la carátula de la póliza. Para este campo, toma el nombre comercial que se presenta como entidad responsable de la póliza. No lo confundas con el nombre del agente, broker o intermediario, que suele estar en otra sección con etiquetas tipo “Agente”, “Intermediario”, “Productor” o el nombre de la agencia.")
    ramo: str|None = Field(default=None, description="El ramo en pólizas de autos suele encontrarse en la carátula o resumen de la póliza, a menudo cerca del número de póliza y la vigencia. Puede estar etiquetado como “Ramo”, “Ramo de seguro”, “Producto” o “Linea de negocio”. En el caso de autos, el ramo puede aparecer como “Autos”, “Automóviles”, “Daños” con una subclasificación de autos, o estar codificado mediante un número o clave interna que se asocia a autos. Busca un bloque donde se describa el tipo de seguro contratado (“Seguro de automóvil”, “Seguro de daños”, etc.). El ramo es el nivel más general de clasificación del seguro dentro de la estructura de productos de la compañía.")
    subRamo: str|None = Field(default=None, description="El subramo es una clasificación más específica dentro del ramo, frecuentemente visible en la misma área que el ramo. Puede aparecer con etiquetas como “Subramo”, “Tipo de vehículo”, “Modalidad” o con una descripción más detallada del producto de autos, por ejemplo, distinguiendo entre “Autos residentes”, “Camiones”, “Motocicletas”, “Pickup uso comercial”, etc. En pólizas de autos, se presenta normalmente como texto descriptivo o como clave acompañada de descripción. Busca esta información cerca del título del producto o debajo del ramo, en la carátula o sección de identificación del seguro. Distingue el subramo de la cobertura (como “Amplia”, “Limitada”), que suele estar en otra línea o tabla.")
    cobertura: str|None = Field(default=None, description="La cobertura principal de la póliza suele estar claramente indicada con términos estándar como “AMPLIA”, “LIMITADA”, “RESPONSABILIDAD CIVIL”, “RC”, “Amplia Plus” u otras denominaciones comerciales. Esta información se ubica normalmente cerca de la descripción del producto, a menudo en mayúsculas o resaltada dentro de un recuadro. Puede estar etiquetada como “Cobertura”, “Plan”, “Paquete” o “Tipo de cobertura”. En pólizas de autos puede aparecer justo debajo del ramo/subramo o en una tabla que enumera coberturas y sumas aseguradas, donde la primera fila o título se refiere al tipo de cobertura general contratada. En ocasiones, aparece en la parte media de la carátula como un texto grande indicando la modalidad (“COBERTURA AMPLIA”, etc.).")
    formaDePago: str|None = Field(default=None, description="La forma de pago está en la sección financiera de la póliza, donde se detallan primas, recargos y calendario de pagos. Puede estar etiquetada como “Forma de pago”, “Método de pago”, “Plan de pagos”, “Periodicidad” o similar. Para pagos de contado se utilizarán palabras como “CONTADO”, “Único”, “Pago único”. Para fraccionados, se usarán términos como “Mensual”, “Trimestral”, “Semestral”, “Anual con financiamiento”, etc. Esta información suele ir junto a la tabla de primas o en un bloque con información del plan de pagos, cerca del total a pagar y los datos de financiamiento. Distingue este campo del medio de cobro específico (tarjeta, domiciliación, etc.), que puede estar en otra sección (“Medio de cobro”, “Forma de cobro”).")
    primaNeta: str|None = Field(default=None, description="La prima neta aparece en el desglose económico de la póliza, generalmente en una tabla de conceptos y montos. Se identifica con etiquetas como “Prima neta”, “Prima Neta”, “Prima base”, “Prima sin impuestos ni recargos”. Suele ser el primer importe monetario de la tabla y representa el costo del seguro antes de impuestos (IVA) y otros cargos (derechos, financiamiento). La cifra normalmente se muestra con separador decimal (punto o coma) y puede aparecer en la fila de resumen de primas, cercana a otros conceptos como recargos, descuentos y el total de prima. Asegúrate de distinguirla de la “prima total” o “prima anual” que incluye impuestos, así como de la suma de financiamiento.")
    primerPago: str|None = Field(default=None, description="En pólizas con información de cobro, el primer pago suele estar indicado en la sección de plan de pagos o tabla de recibos. Se puede etiquetar como “Primer pago”, “Pago inicial”, “1er pago”, “Primer recibo” o similar. En planes de contado, este primer pago coincide con el total a pagar; en planes fraccionados, representa el monto del primer recibo, que puede diferir de los pagos posteriores si hay cargos iniciales. Se ubica cerca de la descripción de periodicidad de pagos y el total financiado. En la tabla, puede ser la primera fila de pagos con su fecha y monto o una cifra de resumen claramente asociada a “primer pago”. Distinguirla de “pago mensual” o “pago posterior” que son montos de las siguientes parcialidades.")
    pagoPosterior: str|None = Field(default=None, description="Este valor se encuentra también en la sección de plan de pagos o en el desglose de financiamiento. Busca etiquetas como “Pagos posteriores”, “Pago subsecuente”, “2do al último pago”, “Pagos restantes” o similar. Representa el monto que se repite en las cuotas que siguen al primer pago en pólizas fraccionadas. Puede mostrarse en una línea tipo “Primer pago: [monto]; Pagos posteriores: [monto] x [número]”. En casos de pago de contado, es común que el valor de pagos posteriores se indique como cero o que no existan filas adicionales en la tabla. No lo confundas con el total financiado ni con la suma de todos los pagos; es el monto unitario de cada pago posterior.")
    descuento: str|None = Field(default=None, description="El descuento, si existe, se muestra en el apartado de desglose de prima, generalmente como un renglón separado con etiquetas como “Descuento”, “Bonificación”, “Descuento comercial”, “Descuento por buen conductor” o similar. Suele aparecer después de la prima neta y antes del subtotal o prima neta ajustada. El monto puede aparecer como valor monetario (negativo o restando al subtotal) y en algunos formatos también se indica el porcentaje aplicado. Ubica este renglón en la tabla de conceptos económicos, junto a otros como recargos, recargos fraccionados, impuesto. Si no hay descuento aplicado, la fila puede aparecer en cero o no mostrarse explícitamente.")
    iva: str|None = Field(default=None, description="El IVA está claramente acreditado en la sección de montos totales, en la misma tabla donde se muestra la prima neta. Se identifica con etiquetas como “I.V.A.”, “IVA”, “Impuesto al Valor Agregado”. Suele ir después de la suma de primas y recargos y antes del total a pagar. Se presenta con formato numérico monetario, y a veces se indica la tasa aplicada (por ejemplo, 16%). Asegúrate de diferenciarlo de otros impuestos o derechos (como derechos de póliza), que se presentan en filas separadas, y de no confundirlo con la “prima total” que ya incorpora el IVA.")
    tasaFinanciamiento: str|None = Field(default=None, description="La tasa de financiamiento se encuentra cuando la póliza tiene pago fraccionado o financiamiento de prima. Aparece en la sección de plan de pagos, a menudo en un recuadro informativo o nota con etiquetas como “Tasa de financiamiento”, “Tasa de interés”, “Costo financiero”, “CAT” (si se incluye). Generalmente se expresa como porcentaje anual o mensual, por ejemplo “Tasa de financiamiento: 0%” o “Tasa de interés: 18% anual”. Puede estar cerca del resumen de cargo por financiamiento o del total financiado. En pólizas pagadas de contado, esta tasa puede indicarse como 0% o simplemente no aparecer. Distinguirla de la tasa de IVA o de porcentajes de descuento, que están en otras líneas con etiquetas distintas.")
    derechoPoliza: str|None = Field(default=None, description="Los derechos de póliza (o derecho de emisión) suelen aparecer como un renglón dentro del desglose de primas e impuestos. Busca etiquetas como “Derecho de póliza”, “Derechos de póliza”, “Gastos de expedición”, “Derecho de emisión”, “Gastos de emisión”. Es un concepto monetario fijo que se suma a la prima neta y a otros cargos antes de calcular el total. Se ubica normalmente después de la prima neta y antes o después del IVA, dependiendo del formato. La cifra es usualmente menor que la prima y está claramente separada de otros conceptos como recargo por pago fraccionado. No lo confundas con comisiones de agente o con cargos bancarios, que rara vez se muestran en la carátula.")
    total: str|None = Field(default=None, description="El total a pagar se indica de forma destacada en la sección económica de la póliza, comúnmente en negritas o con tipografía más grande. Está etiquetado como “Total”, “Total a pagar”, “Total de la póliza”, “Importe total” o “Total anual”. Representa la suma de la prima neta, derechos, impuestos y, en su caso, financiamiento. Puede aparecer al final de la tabla de conceptos, como la última fila de montos, o en un recuadro de resumen separado. En pólizas con pago fraccionado, puede haber un “total financiado” o “total a pagar en el año”; verifica la etiqueta para elegir el total global de la póliza, no el monto de una sola cuota. Distingue este valor del “total a financiar” si está separado, y del “saldo” que podría existir en documentos de renovación.")
    cargoPorFinanciamiento: str|None = Field(default=None, description="Este campo se refiere al importe monetario adicional por financiamiento de la prima cuando no se paga de contado. Se localiza en el área de detalles de pagos o en la tabla de conceptos económicos con etiquetas como “Cargo por financiamiento”, “Recargo por pago fraccionado”, “Intereses”, “Costo de financiamiento”. Suele aparecer como una línea intermedia entre la prima neta (o subtotal) y el total, o como nota asociada al plan de pagos donde se indica cuánto del total corresponde al financiamiento. En pólizas con pago de contado, es común que este importe se muestre como cero o que la línea no aparezca. No lo confundas con recargos por coberturas opcionales ni con derechos de póliza.")
    rfcAsegurado: str|None = Field(default=None, description="El RFC del asegurado aparece en la sección de datos del contratante/asegurado, normalmente cerca del nombre completo y el domicilio. La sección puede llamarse “Datos del asegurado”, “Contratante”, “Asegurado”, “Cliente” o similar. El RFC se etiqueta como “R.F.C.”, “RFC” o “Registro Federal de Contribuyentes”. El valor suele ser una cadena alfanumérica de 12 o 13 caracteres (4 letras + 6 dígitos + 2 o 3 caracteres de homoclave) sin espacios. Este bloque de información suele estar en la parte superior o intermedia de la carátula, a veces dentro de un recuadro con varios campos (nombre, RFC, domicilio, teléfono, correo). No lo confundas con el RFC de la aseguradora o del agente, que pueden aparecer en notas fiscales o en el pie de página con etiquetas diferentes (por ejemplo, RFC de la empresa).")
    nombreAsegurado: str|None = Field(default=None, description="El nombre del asegurado/contratante está en la misma sección de datos personales donde se encuentra el RFC. Busca un bloque con título “Asegurado”, “Contratante”, “Nombre del asegurado”, “Nombre/Razón social” o equivalente. El valor suele estar en mayúsculas, compuesto por nombre(s) y apellidos, o razón social si se trata de persona moral. Aparece al inicio del bloque de datos de cliente, precediendo a otros campos como RFC, domicilio, teléfono. En algunos formatos, el nombre está inmediatamente a la derecha de la etiqueta y puede abarcar más de una línea si es largo. Distingue este nombre del nombre del beneficiario preferente, del agente o de un conductor habitual, que se muestran en secciones específicas con sus propias etiquetas.")
    numeroSerie: str|None = Field(default=None, description="El número de serie del vehículo (VIN) se ubica en la sección de descripción del vehículo asegurado. Busca un apartado con títulos como “Datos del vehículo”, “Vehículo asegurado”, “Características del vehículo”. Este bloque incluye campos como marca, submarca, modelo, número de serie, placas, uso, etc. El número de serie se etiqueta como “No. de serie”, “Número de serie”, “VIN”, “Serie” o similar. Es una cadena alfanumérica de 17 caracteres, sin espacios, que puede incluir letras y números. Aparece junto a otros identificadores del vehículo, usualmente en una tabla o lista alineada. Asegúrate de no confundirlo con números de motor, folios internos o códigos de versión que también pueden ser alfanuméricos pero con etiquetas diferentes.")
    modelo: str|None = Field(default=None, description="El modelo corresponde usualmente al año modelo del vehículo. En la sección de “Datos del vehículo” o “Vehículo asegurado”, busca el campo etiquetado como “Modelo”, “Año modelo”, “Año” o similar. El valor suele ser un año de cuatro dígitos (por ejemplo, 2017) y se acompaña de otros datos como marca, submarca, tipo de vehículo. Puede estar en línea con la descripción del vehículo (por ejemplo, “Marca/Submarca/Modelo”) o como columna separada en una tabla. Asegúrate de no confundirlo con el código de versión o con el año de fabricación (si se muestran ambos); en pólizas de autos mexicanas típicamente se refiere al año modelo comercial del automóvil.")
    numeroPlacas: str|None = Field(default=None, description="El número de placas también se encuentra en la sección de “Datos del vehículo”. Allí se listan campos como marca, modelo, serie, color y placas. Este campo se etiqueta como “Placas”, “No. de placas”, “Número de placas” o equivalente. El valor consiste en una combinación alfanumérica (letras y números) y, a veces, guiones o espacios, de longitud variable dependiendo del estado. Puede ir acompañado de la entidad federativa emisora. En la tabla, suele ubicarse en la misma fila que el VIN o muy cerca. No lo confundas con el número de póliza, de motor u otras claves similares.")
    adaptaciones: str|None = Field(default=None, description="Las adaptaciones o equipo especial del vehículo se describen, si existen, en la sección que detalla características adicionales del vehículo. El campo puede estar etiquetado como “Adaptaciones”, “Equipo especial”, “Conversiones”, “Modificaciones”, “Accesorios” o similar. A veces aparece como un campo de texto libre debajo de los datos principales del vehículo o como un renglón dentro de la tabla de coberturas específicas de adaptaciones. En muchos casos, si el vehículo no tiene adaptaciones aseguradas, este campo aparece vacío, con un texto como “Ninguna”, “No aplica” o simplemente sin contenido. Se diferencia de la descripción estándar del vehículo (marca/modelo/versión) porque hace referencia a modificaciones adicionales o equipo no original.")
    version: str|None = Field(default=None, description="La versión del vehículo suele figurar como un código o descripción más detallada dentro de la sección de “Datos del vehículo”. Puede estar etiquetada como “Versión”, “Clave versión”, “Código versión”, “Descripción detallada”, “Submodelo” o aparecer integrada en una línea que describe el vehículo junto con marca y submarca. En algunos formatos de aseguradoras, se muestra como un código numérico o alfanumérico interno que identifica la versión exacta del vehículo según el catálogo de la compañía. Puede situarse en la misma fila que el modelo o en una columna separada en la tabla. No lo confundas con el número de serie (VIN), que también es alfanumérico pero está etiquetado explícitamente como serie o VIN.")
    beneficiarioPreferente: str|None = Field(default=None, description="El beneficiario preferente (también llamado acreedor prendario) se detalla en una sección específica, generalmente cercana a los datos del asegurado o del vehículo. Las etiquetas habituales son “Beneficiario preferente”, “Acreedor prendario”, “Financiera”, “Arrendadora” o “Banco”. El campo puede contener el nombre de una institución financiera, arrendadora o banco cuando el vehículo está financiado o en arrendamiento. Aparece como nombre de persona moral (por ejemplo, “Banco X, S.A.”) y puede incluir datos adicionales como RFC o domicilio, aunque normalmente sólo se muestra la razón social. Si no existe beneficiario preferente, el campo puede verse en blanco, con texto “Ninguno”, “No aplica” o no aparecer la sección. Ubica este dato en la carátula o en un bloque intermedio del documento, no en las secciones de beneficiarios de vida ni en cláusulas generales, que son diferentes.")




# prompt_template_dict = {
#     "poliza": "Extrae el número de póliza principal del documento de QUÁLITAS. Busca etiquetas como: \"Póliza\", \"Póliza No.\", \"No. de póliza\", \"Núm. de póliza\". Reglas: 1) Prioriza el número ubicado en el encabezado o cerca del logo/razón social de QUÁLITAS. 2) Excluye números de endoso, cotización o siniestro. 3) Devuelve solo dígitos sin espacios ni guiones. 4) Si hay varios, toma el de mayor prominencia o el que esté junto a la palabra Póliza. Si no existe, devuelve cadena vacía.",
#     "inicioPeriodoVigencia": "Para extraer la fecha de inicio del periodo de vigencia:\n- Localiza el bloque del documento donde se describa la vigencia de la póliza; suele estar en la sección de \"Datos de la Póliza\" o \"Vigencia\", generalmente cerca del encabezado donde se muestra el número de póliza.\n- Busca expresiones típicas como: \"Vigencia\", \"Periodo de vigencia\", \"Desde\", \"Fecha de inicio\", \"Inicio de vigencia\", \"Desde las 12:00 hrs del\" o similares.\n- Dentro de ese bloque, identifica la fecha asociada al comienzo del periodo, muchas veces presentada en un formato tipo: dd/mm/aaaa, dd-mm-aaaa, o con el mes en texto (por ejemplo: \"06 de julio de 2022\").\n- Cuando el texto incluya un rango (por ejemplo: \"Vigencia: del xx/xx/xxxx al xx/xx/xxxx\"), toma la primera fecha del rango como fecha de inicio.\n- Si el documento incluye la hora (por ejemplo \"12:00\" o \"12:00 hrs\" o similar) y zona horaria, considera que la fecha de inicio puede necesitar normalización a un formato de fecha y hora estandarizado.\n\nInstrucciones de extracción estructurada:\n- Convierte la fecha encontrada al formato de fecha y hora ISO 8601 con zona horaria, siguiendo el patrón: \"YYYY-MM-DDThh:mm:ss-06:00\" siempre que el documento sea de México y la zona horaria implícita sea la del país; si el documento explicita otra zona, úsala en el offset.\n- Si el documento sólo muestra la fecha (sin hora), asume la hora estándar de inicio de vigencia que indique el documento (típicamente \"12:00\"), y si se indica explícitamente una hora distinta, úsala.\n- Usa ceros a la izquierda para día y mes de un solo dígito.\n- No incluyas texto adicional como \"hrs\", \"del\", \"a las\", etc.; sólo la fecha y hora normalizadas.\n",
#     "finalPeriodoVigencia": "Plantilla de prompt: Extrae la fecha de fin de vigencia de la póliza. Busca frases como: Vigencia del... al..., Fin de vigencia, Hasta, Vigente hasta. Si aparece el rango del X al Y, toma Y como fin. Convierte la fecha a timestamp Unix en segundos a las 00:00:00 hora America/Mexico_City. Devuelve solo el número. Si no se encuentra, devuelve vacío. ",
#     "aseguradora": "Extrae el nombre de la aseguradora emisora. En documentos de esta clase debe ser \"QUÁLITAS\" o su razón social completa (por ejemplo, \"QUÁLITAS Compañía de Seguros, S.A. de C.V.\"). Devuelve la marca corta \"QUÁLITAS\" si aparece; si no, devuelve el nombre tal como esté impreso. Sin etiquetas adicionales. Si no existe, cadena vacía.",
#     "ramo": "Extrae el ramo (por ejemplo: Autos, Daños, Vida). Busca etiquetas: \"Ramo\", \"Ramo/Producto\". Devuelve el texto tal como aparece, en mayúsculas si ya viene así. Si no se especifica, devuelve cadena vacía.",
#     "subRamo": "Extrae el subramo o producto/plan específico. Busca: \"Subramo\", \"Producto\", \"Plan\". Devuelve el texto exacto sin etiquetas. Si no existe, cadena vacía.",
#     "cobertura": "Extrae la cobertura/paquete principal (ej.: Amplia, Limitada, RC). Busca: \"Cobertura\", \"Paquete\". Prefiere el valor indicado en el resumen de la póliza. Devuelve solo el nombre de la cobertura. Si no existe, cadena vacía.",
#     "formaDePago": "Extrae la forma o plan de pago. Busca: \"Forma de pago\", \"Plan de pagos\", \"Modalidad de pago\". Valores típicos: CONTADO, MENSUAL, SEMESTRAL, ANUAL, TARJETA, TRANSFERENCIA. Devuelve el valor textual exactamente como aparece (sin etiquetas). Si no existe, cadena vacía.",
#     "primaNeta": "Extrae el importe de \"Prima Neta\". Busca la etiqueta exacta \"Prima Neta\". Devuelve solo el número en formato 12345.67 (punto decimal, sin símbolo $, sin espacios, con separadores de miles opcionales removidos). Si no existe, cadena vacía.",
#     "primerPago": "Extrae el importe de \"Primer pago\" o \"Pago inicial\". Busca: \"Primer pago\", \"Pago inicial\". Devuelve número en formato 12345.67 (sin $ ni comas de miles). Si no existe, cadena vacía.",
#     "pagoPosterior": "Extrae el importe de \"Pago(s) posterior(es)\" o \"Pagos subsecuentes\". Busca: \"Pago(s) posterior(es)\", \"Pagos subsecuentes\", \"Pago(s) siguientes\". Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, devuelve 0 si el plan es CONTADO; de lo contrario, cadena vacía.",
#     "descuento": "Extrae el importe de \"Descuento\" o \"Bonificación\" si se muestra en el desglose. Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, devuelve 0.",
#     "iva": "Extrae el IVA del desglose. Busca: \"IVA\" o \"I.V.A.\" asociado a importes. Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, cadena vacía.",
#     "tasaFinanciamiento": "Extrae el monto asociado a financiamiento/bonificación por financiamiento. Busca etiquetas como: \"Tasa de financiamiento\", \"Costo/ cargo por financiamiento\", \"Bonificación por pago de contado\". Si aparece como monto negativo, conserva el signo. Devuelve número en formato 12345.67 (sin $ ni comas). Si solo hay porcentaje y no monto, devuelve el porcentaje con el signo % (por ejemplo, 10%). Si no existe, cadena vacía.",
#     "derechoPoliza": "Extrae \"Derecho(s) de póliza\". Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, devuelve 0.",
#     "total": "Extrae el \"Total\" o \"Total a pagar\" del resumen de cobro. Prioriza el total final tras impuestos, derechos y cargos. Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, cadena vacía.",
#     "cargoPorFinanciamiento": "Extrae el \"Cargo por financiamiento\" (si se separa explícitamente del total). Devuelve número en formato 12345.67 (sin $ ni comas, conserva signo si es negativo). Si no existe, devuelve 0.",
#     "rfcAsegurado": "Extrae el RFC del Asegurado (no del Agente ni de la Aseguradora). Busca cerca de \"Asegurado\" o \"Contratante\". Valida con patrón: [A-Z&Ñ]{3,4}\\d{6}[A-Z0-9]{2,3}. Devuelve en mayúsculas sin espacios. Si hay dos (contratante y asegurado), prioriza el de Asegurado. Si no existe, cadena vacía.",
#     "nombreAsegurado": "Extrae el nombre completo del Asegurado. Busca: \"Asegurado:\", \"Nombre del asegurado\". Si aparecen Contratante y Asegurado, devuelve el de Asegurado. Respeta mayúsculas/acentos tal como en el documento. Devuelve solo el nombre sin etiquetas. Si no existe, cadena vacía.",
#     "numeroSerie": "Extrae el número de serie/VIN del vehículo. Busca: \"No. de serie\", \"Núm. de serie\", \"VIN\". Valida longitud 17 con A-Z y 0-9 (excluye I, O, Q si es posible). Devuelve en mayúsculas sin espacios. Si no existe, cadena vacía.",
#     "modelo": "Extrae el año modelo del vehículo. Busca: \"Modelo\" o \"Año\" cercano a los datos del vehículo. Devuelve un número de cuatro dígitos (por ejemplo, 2017). Si no existe, cadena vacía.",
#     "numeroPlacas": "Extrae el número de placas. Busca: \"Placas\", \"No. de placas\". Devuelve en mayúsculas, sin espacios adicionales. Si no existe, cadena vacía.",
#     "adaptaciones": "Extrae el campo de \"Adaptaciones y conversiones\" o \"Adaptaciones\" si aparece como texto/descripción. Si solo se reporta un monto sin descripción, devuelve ese texto/monto; si no hay adaptaciones declaradas, devuelve cadena vacía.",
#     "version": "Extrae la versión o clave vehicular. Busca: \"Versión\", \"Clave versión\", \"Clave vehicular\", \"Código\" cercano a datos del vehículo. Devuelve exactamente el código/texto mostrado (por ejemplo, 02134). Si no existe, cadena vacía.",
#     "beneficiarioPreferente": "Extrae el Beneficiario/Acreedor preferente (por ejemplo, una institución financiera). Busca: \"Beneficiario preferente\", \"Acreedor preferente\". Si hay varios, devuelve el primero principal. Devuelve solo el nombre de la entidad. Si no existe, cadena vacía."
#   }

def safe_description(val):
    # Ensure the description is a string and escape problematic quotes
    if not isinstance(val, str):
        val = str(val)
    return val.replace('"', "'")

# poliza: str = Field(description="Para extraer el número de póliza de un documento no estructurado, busca una sección donde se mencione la palabra \"póliza\" o \"No. de póliza\", que por lo general aparece en la parte superior del documento, cerca de los datos generales, nombre del asegurado o datos de la aseguradora. El número suele estar justo después del título correspondiente y se encuentra en un formato completamente numérico, típicamente resaltado o en negritas. Si existen patrones visuales como tablas, identifica la celda con el encabezado relacionado e identifica el valor que le sigue inmediatamente a la derecha o debajo. Si hay varias pólizas o números, enfócate en el que esté explícitamente etiquetado como \"Póliza\" principal.")
# class GeneralInvoiceInformation(BaseModel):
#     # Qualitas insurance example fields
#     poliza: str|None = Field(description="Para extraer el campo «poliza» de documentos similares, usa el siguiente prompt como plantilla, adaptándolo al formato exacto del archivo que tengas:\n\n---\n\n[INSTRUCCIONES GENERALES]\nAnaliza el documento proporcionado. Es un documento de seguro de automóvil de la aseguradora QUÁLITAS (u otra aseguradora similar). Tu objetivo es identificar el número de póliza.\n\nDebes basarte exclusivamente en el contenido visible del documento (texto, tablas, encabezados, pies de página, recuadros, etc.). Ignora cualquier conocimiento externo.\n\nDevuélveme ÚNICAMENTE el valor del número de póliza, sin etiquetas, sin texto adicional, sin comentarios, sin espacios iniciales ni finales.\n\n[ENFOQUE POR DISEÑO Y PATRONES DEL DOCUMENTO]\n1. Localiza la sección principal del documento donde aparezcan datos como:\n   - Nombre de la aseguradora (por ejemplo, «QUÁLITAS» en logotipo o encabezado).\n   - Datos de identificación del contrato: póliza, vigencia, forma de pago, etc.\n\n2. Busca específicamente textos o etiquetas que contengan alguna de las siguientes variantes (pueden estar en mayúsculas, minúsculas o combinadas):\n   - «PÓLIZA»\n   - «Poliza»\n   - «No. de póliza»\n   - «Núm. de póliza»\n   - «Número de póliza»\n   - «PÓLIZA No.»\n   - O abreviaturas similares asociadas claramente al contrato de seguro.\n\n3. Observa el diseño típico:\n   - El número de póliza suele aparecer en la parte superior del documento, cercano al logo de la aseguradora o a un recuadro con datos generales.\n   - Puede estar en una tabla de cabecera, en una fila junto a otros campos como: «Vigencia», «Forma de pago», «Ramo», «Subramo».\n   - Puede estar alineado a la derecha o dentro de un recuadro destacado.\n\n4. Identifica el valor asociado a la etiqueta de póliza:\n   - Una vez localizada la etiqueta (por ejemplo: «PÓLIZA:»), el valor que buscas será el texto numérico que la acompaña, normalmente:\n     - Una cadena numérica de varios dígitos.\n     - Puede contener espacios, guiones o caracteres de separación, pero sigue siendo un identificador único.\n   - El valor suele estar:\n     - En la misma línea, después de la etiqueta.\n     - O en la celda contigua de una tabla.\n     - O inmediatamente debajo de la etiqueta en documentos con diseño apilado (etiqueta arriba, valor abajo).\n\n5. Desambiguación:\n   - Asegúrate de no confundir el número de póliza con otros números como:\n     - Número de serie del vehículo (VIN), que suele ser una combinación de letras y números más larga.\n     - Placas del vehículo (suelen contener letras y números con guion o sin él).\n     - RFC del asegurado (formato alfanumérico con patrón fiscal).\n     - Número de versión o código de producto.\n   - Si aparecen varios números cerca de la palabra «póliza», selecciona el que esté directamente etiquetado como tal o más claramente asociado con «PÓLIZA».\n\n[VALIDACIÓN DEL FORMATO]\n- Verifica que el valor extraído:\n  - No incluya la palabra «Póliza», «No.», «Núm.», «Número», ni dos puntos.\n  - No incluya espacios iniciales o finales.\n  - No incluya otros textos ajenos (por ejemplo, fecha, nombre, etc.).\n\n[RESPUESTA]\nDevuelve solo el número de póliza tal como aparece en el documento (respetando su secuencia de dígitos y posibles separadores internos si los hubiera), sin ningún texto adicional.\n\n---\n")
#     inicioPeriodoVigencia: str|None = Field(default="", description="Para extraer la fecha de inicio del periodo de vigencia:\n- Localiza el bloque del documento donde se describa la vigencia de la póliza; suele estar en la sección de \"Datos de la Póliza\" o \"Vigencia\", generalmente cerca del encabezado donde se muestra el número de póliza.\n- Busca expresiones típicas como: \"Vigencia\", \"Periodo de vigencia\", \"Desde\", \"Fecha de inicio\", \"Inicio de vigencia\", \"Desde las 12:00 hrs del\" o similares.\n- Dentro de ese bloque, identifica la fecha asociada al comienzo del periodo, muchas veces presentada en un formato tipo: dd/mm/aaaa, dd-mm-aaaa, o con el mes en texto (por ejemplo: \"06 de julio de 2022\").\n- Cuando el texto incluya un rango (por ejemplo: \"Vigencia: del xx/xx/xxxx al xx/xx/xxxx\"), toma la primera fecha del rango como fecha de inicio.\n- Si el documento incluye la hora (por ejemplo \"12:00\" o \"12:00 hrs\" o similar) y zona horaria, considera que la fecha de inicio puede necesitar normalización a un formato de fecha y hora estandarizado.\n\nInstrucciones de extracción estructurada:\n- Convierte la fecha encontrada al formato de fecha y hora ISO 8601 con zona horaria, siguiendo el patrón: \"YYYY-MM-DDThh:mm:ss-06:00\" siempre que el documento sea de México y la zona horaria implícita sea la del país; si el documento explicita otra zona, úsala en el offset.\n- Si el documento sólo muestra la fecha (sin hora), asume la hora estándar de inicio de vigencia que indique el documento (típicamente \"12:00\"), y si se indica explícitamente una hora distinta, úsala.\n- Usa ceros a la izquierda para día y mes de un solo dígito.\n- No incluyas texto adicional como \"hrs\", \"del\", \"a las\", etc.; sólo la fecha y hora normalizadas.\n")
#     finalPeriodoVigencia: str|None = Field(default="", description="Plantilla de prompt: Extrae la fecha de fin de vigencia de la póliza. Busca frases como: Vigencia del... al..., Fin de vigencia, Hasta, Vigente hasta. Si aparece el rango del X al Y, toma Y como fin. Convierte la fecha a timestamp Unix en segundos a las 00:00:00 hora America/Mexico_City. Devuelve solo el número. Si no se encuentra, devuelve vacío. ") 
#     aseguradora: str|None = Field(default="", description="Plantilla de prompt: Identifica el nombre de la aseguradora emisora. Busca en encabezado, logotipo y razón social: QUÁLITAS, Quálitas Compañía de Seguros, S.A. de C.V., Qualitas. Normaliza a QUÁLITAS. Devuelve solo el nombre normalizado. Si no se encuentra, devuelve vacío.")
#     ramo: str|None = Field(default="", description="Plantilla de prompt: Extrae el ramo del seguro. Busca etiquetas como: Ramo, Línea de negocio. En pólizas de auto suele ser Automóviles o Autos. Si no hay etiqueta explícita pero aparece información vehicular (VIN/NIV de 17 caracteres, placas, modelo), establece Automóviles. Devuelve solo el valor del ramo. Si no procede, devuelve vacío.")
#     subRamo: str|None = Field(default="", description="Plantilla de prompt: Extrae el subramo o uso. Busca etiquetas como: Subramo, Uso, Tipo de uso, Residente/Turista, Particular/Servicio Público. Devuelve el texto tal como aparece, en mayúsculas. Si no se encuentra, devuelve vacío.")
#     cobertura: str|None = Field(default="", description="Plantilla de prompt: Extrae el plan/paquete de cobertura contratada. Busca etiquetas: Cobertura, Paquete, Plan, con valores típicos Amplia, Limitada, Responsabilidad Civil, RC. Si hay varias menciones, toma la que esté junto a la identificación del vehículo o del contrato. Devuelve solo el nombre de la cobertura. Si no se encuentra, devuelve vacío.")
#     formaDePago: str|None = Field(default="", description="Plantilla de prompt: Extrae la forma de pago. Busca etiquetas: Forma de pago, Plan de pagos, Modalidad de pago. Normaliza a uno de: CONTADO, MENSUAL, BIMESTRAL, TRIMESTRAL, SEMESTRAL, ANUAL, FINANCIADO. Si se menciona una tarjeta o banco pero no la periodicidad, usa CONTADO si se observa un único pago total. Devuelve solo el valor normalizado. Si no se encuentra, devuelve vacío.")
#     primaNeta: str|None = Field(default="", description="Plantilla de prompt: Extrae el importe de Prima Neta. Busca etiquetas: Prima Neta, Subtotal prima. Elige el monto del desglose de primas, no el total. Normaliza eliminando símbolo de moneda y espacios; conserva signo si existe y dos decimales con punto. Devuelve solo el número como texto. Si no se encuentra, devuelve vacío. ")
#     primerPago: str|None = Field(default="", description="Plantilla de prompt: Extrae el monto del Primer Pago. Busca etiquetas: Primer pago, Primer pago con inscripción o similar. Si la forma de pago es CONTADO, el Primer Pago suele ser igual al Total. Normaliza eliminando símbolo de moneda y separadores de miles; dos decimales con punto. Devuelve solo el número como texto. Si no se encuentra, devuelve vacío. ")
#     pagoPosterior: str|None = Field(default="", description="Plantilla de prompt: Extrae el monto de Pago(s) Posterior(es). Busca etiquetas: Pagos posteriores, Pago(s) posterior(es), Pagos subsecuentes. Si la forma de pago es CONTADO, devuelve 0. Si aparecen varios pagos posteriores, devuelve el importe unitario por pago, no la suma. Normaliza a número con dos decimales y punto. Devuelve solo el número como texto o 0 si no aplica. ")
#     descuento: str|None = Field(default="", description="Plantilla de prompt: Extrae el total de Descuento(s) aplicados. Busca etiquetas: Descuento, Bonificación, Promoción en el desglose. Si hay múltiples descuentos, suma sus importes. Normaliza a número con dos decimales, punto decimal y sin símbolo de moneda. Si no hay descuento, devuelve 0. Devuelve solo el número como texto. ")
#     iva: str|None = Field(default="", description="Plantilla de prompt: Extrae el IVA del desglose de primas. Busca etiquetas: IVA, Impuesto al Valor Agregado y toma el monto (no el porcentaje). Normaliza a número con dos decimales y punto. Devuelve solo el número como texto. Si no aplica, devuelve 0. ")
#     tasaFinanciamiento: str|None = Field(default="", description="Plantilla de prompt: Extrae el importe monetario por financiamiento (recargo o descuento). Busca etiquetas: Tasa de financiamiento, Recargo por financiamiento, Intereses por financiamiento en el desglose económico. Si aparece también un porcentaje, devuelve el monto en dinero, conservando el signo si es descuento (negativo). Normaliza a número con dos decimales y punto. Si no aplica, devuelve 0. ")
#     derechoPoliza: str|None = Field(default="", description="Plantilla de prompt: Extrae el importe de Derecho de Póliza (gastos de expedición). Busca etiquetas: Derecho de póliza, Gastos de expedición. Normaliza a número con dos decimales, punto decimal. Devuelve solo el número como texto. Si no aparece, devuelve 0. ")
#     total: str|None = Field(default="", description="Plantilla de prompt: Extrae el Total a pagar de la póliza. Busca etiquetas: Total, Total a pagar, Prima total y toma el gran total del recibo o desglose. Normaliza a número con dos decimales y punto. Devuelve solo el número como texto. Si hay varios totales (por pagos parciales), elige el total del periodo actual contratado. ")
#     cargoPorFinanciamiento: str|None = Field(default="", description="Plantilla de prompt: Extrae el Cargo por Financiamiento si se presenta como línea separada del desglose. Busca etiquetas: Cargo por financiamiento, Recargo por financiamiento. Prioriza el monto monetario, no el porcentaje. Normaliza a número con dos decimales y punto. Si no existe o ya está reflejado en otra línea, devuelve 0. ")
#     rfcAsegurado: str|None = Field(default="", description="Plantilla de prompt: Extrae el RFC del Asegurado. Busca en secciones: Datos del asegurado o Contratante con etiqueta RFC. Prioriza el RFC del Asegurado; si no existe, usa el del Contratante. Valida formato mexicano de 12 o 13 caracteres alfanuméricos (con homoclave). Devuelve en mayúsculas sin espacios. Si no se encuentra, devuelve vacío.")
#     nombreAsegurado: str|None = Field(default="", description="Plantilla de prompt: Extrae el nombre del Asegurado. Busca etiquetas: Asegurado, Nombre del asegurado. Si no aparece, usa el Contratante. Evita capturar el nombre del agente o beneficiario. Devuelve el nombre completo tal como aparece, en mayúsculas si así está. Si no se encuentra, devuelve vacío.")
#     numeroSerie: str|None = Field(default="", description="Plantilla de prompt: Extrae el Número de Serie del vehículo (VIN/NIV). Busca etiquetas: Número de serie, No. de serie, VIN, NIV. Debe ser un identificador alfanumérico de 17 caracteres. Devuelve en mayúsculas, sin espacios. Si no se encuentra, devuelve vacío.")
#     modelo: str|None = Field(default="", description="Plantilla de prompt: Extrae el modelo/año del vehículo. Busca etiquetas: Modelo, Año modelo, Año junto con el vehículo. Devuelve cuatro dígitos (aaaa). Si hay varios años (fabricación/modelo), elige el Modelo. Si no se encuentra, devuelve vacío.")
#     numeroPlacas: str|None = Field(default="", description="Plantilla de prompt: Extrae el número de placas del vehículo. Busca etiquetas: Placas, No. de placa(s). Devuelve el texto alfanumérico en mayúsculas, sin espacios adicionales. Si no se encuentra, devuelve vacío.")
#     adaptaciones: str|None = Field(default="", description="Plantilla de prompt: Extrae las Adaptaciones o Equipo Especial del vehículo si existen. Busca etiquetas: Adaptaciones, Equipo especial. Si aparece N/A, No aplica o está en blanco, devuelve vacío. Devuelve el texto tal como aparece (hasta 100 caracteres). Si no se encuentra, devuelve vacío.")
#     version: str|None = Field(default="", description="Plantilla de prompt: Extrae la Versión o Clave de versión del vehículo. Busca etiquetas: Versión, Clave versión, Vers. Puede ser un código numérico o alfanumérico. Devuelve el valor sin etiquetas. Si no se encuentra, devuelve vacío.")
#     beneficiarioPreferente: str|None = Field(default="", description="Plantilla de prompt: Extrae el Beneficiario Preferente o Acreedor Prendario. Busca etiquetas: Beneficiario preferente, Acreedor prendario, Beneficiario en la sección de datos financieros del vehículo. Devuelve el nombre de la institución si existe. Si no aplica o está vacío, devuelve vacío.")
    
#     # Chubb
#     # poliza: str = Field(description="Para extraer el número de póliza:\n- Recorre visualmente las primeras secciones del documento, normalmente en el encabezado o bloque superior.\n- Localiza un bloque con título o etiqueta similar a: \"PÓLIZA\", \"No. de póliza\", \"Nº de Póliza\", \"Número de póliza\", o su versión abreviada (por ejemplo: \"Póliza:\" seguido de un código alfanumérico).\n- Presta atención a que en pólizas de autos suele haber un encabezado de compañía (logo + nombre de la aseguradora) y cerca de ese encabezado aparecen datos clave: número de póliza, tipo de seguro, contratante, etc.\n- Identifica el valor que contenga una combinación de letras mayúsculas seguidas de números (formato similar a GOxxxxxxxx), normalmente sin espacios internos, y asociado directamente al texto de etiqueta de póliza.\n- Ignora otros identificadores similares que estén claramente etiquetados como: \"Certificado\", \"Endoso\", \"Cotización\", \"Referencia\", \"Cliente\", o \"Siniestro\".\n- Si el documento contiene varias pólizas o endosos, elige el número de póliza principal, que suele aparecer en el título general o en un recuadro principal y no en tablas secundarias o secciones de detalle.\n\nInstrucciones de extracción estructurada:\n- Devuelve únicamente el texto exacto del número de póliza tal y como aparece impreso (sin agregar prefijos ni palabras adicionales, sin recortar caracteres internos).\n- Si hay más de un número etiquetado como póliza, selecciona el que aparezca en el encabezado principal o en el primer bloque de datos generales.\n- No incluyas puntos, comas u otros signos de puntuación que no formen parte del número de póliza.\n",)
#     # inicioPeriodoVigencia: str = Field(default="", description="Para extraer la fecha de inicio del periodo de vigencia:\n- Localiza el bloque del documento donde se describa la vigencia de la póliza; suele estar en la sección de \"Datos de la Póliza\" o \"Vigencia\", generalmente cerca del encabezado donde se muestra el número de póliza.\n- Busca expresiones típicas como: \"Vigencia\", \"Periodo de vigencia\", \"Desde\", \"Fecha de inicio\", \"Inicio de vigencia\", \"Desde las 12:00 hrs del\" o similares.\n- Dentro de ese bloque, identifica la fecha asociada al comienzo del periodo, muchas veces presentada en un formato tipo: dd/mm/aaaa, dd-mm-aaaa, o con el mes en texto (por ejemplo: \"06 de julio de 2022\").\n- Cuando el texto incluya un rango (por ejemplo: \"Vigencia: del xx/xx/xxxx al xx/xx/xxxx\"), toma la primera fecha del rango como fecha de inicio.\n- Si el documento incluye la hora (por ejemplo \"12:00\" o \"12:00 hrs\" o similar) y zona horaria, considera que la fecha de inicio puede necesitar normalización a un formato de fecha y hora estandarizado.\n\nInstrucciones de extracción estructurada:\n- Convierte la fecha encontrada al formato de fecha y hora ISO 8601 con zona horaria, siguiendo el patrón: \"YYYY-MM-DDThh:mm:ss-06:00\" siempre que el documento sea de México y la zona horaria implícita sea la del país; si el documento explicita otra zona, úsala en el offset.\n- Si el documento sólo muestra la fecha (sin hora), asume la hora estándar de inicio de vigencia que indique el documento (típicamente \"12:00\"), y si se indica explícitamente una hora distinta, úsala.\n- Usa ceros a la izquierda para día y mes de un solo dígito.\n- No incluyas texto adicional como \"hrs\", \"del\", \"a las\", etc.; sólo la fecha y hora normalizadas.\n",)
#     # finalPeriodoVigencia: str = Field(default="", description="Para extraer la fecha de fin del periodo de vigencia:\n- En la misma sección donde se encuentra la vigencia, identifica el rango completo de fechas; suele aparecer como: \"Vigencia: del [fecha inicio] al [fecha fin]\" o \"Desde [fecha inicio] hasta [fecha fin]\".\n- Localiza la segunda fecha del rango, que corresponde al término de la vigencia.\n- También pueden utilizarse frases como: \"Hasta\", \"Fecha de término\", \"Fin de vigencia\", \"Término de vigencia\" o variantes equivalentes.\n- Presta atención a que el diseño muchas veces alinea las fechas de inicio y fin en una misma línea o en dos columnas bajo un título común \"Vigencia\" (por ejemplo, una columna \"Desde\" y otra \"Hasta\"). La fecha de fin se ubicará en la posición asociada a \"Hasta\" o \"al\".\n- Si se indica una hora específica para el término (por ejemplo \"a las 12:00 hrs\"), esta hora debe ser capturada junto con la fecha.\n\nInstrucciones de extracción estructurada:\n- Normaliza la fecha y hora encontradas al mismo formato ISO 8601 con zona horaria: \"YYYY-MM-DDThh:mm:ss-06:00\" u otro offset si el documento lo especifica claramente.\n- Si sólo se muestra la fecha, asume la misma hora estándar indicada en el documento para el término de vigencia (usualmente \"12:00\"), salvo que se indique explícitamente una distinta.\n- Usa ceros a la izquierda para día y mes de un solo dígito.\n- No incluyas palabras de enlace como \"al\", \"hasta\", \"a las\", ni sufijos como \"hrs\" en el valor final; únicamente fecha y hora en formato estándar.\n")
  
   
template_extractor_prompt =f"""
    Eres un experto en extraer datos estructurados de documentos no estructurados.
    
    # Seguiras el siguiente workflow
    1. (Mandatorio): Consulta la base de datos vectorial para extraer la información.
    2. La información extraida la estructuraras como un texto en lenguaje natural.
    3. Regresa el texto con la información. 

    # Si no encontraste la información, expresa en el texto, que dicha información no fue encontrada.

    # El cliente valora mas la "precisión" que la rapidez, así que tómate tu tiempo para validar cada campo.
    
    Información a encontrar:
    """

template_validator_prompt =f"""
    Eres un experto en extraer datos estructurados de documentos no estructurados.

    # Contexto: 
    Ayudaras a extraer información a partir de un texto con la información,
    con la informaicón que encuentres del texto, llenaras los campos que
    se te soliciten (structure outputs). 

    Es importante que si no encuentras la información en el texto para un campo, 
    llenes dicho campo con un `None` 
      

    Texto con la información: 
    """


def execute_test():
    path_to_prompt ="D:/DOCUMENTS/self_study/Agents/langchain_learning/automatic_program_engineering/autogenerated_files/AutogeneratedPrompt.json"
    prompt_template_dict = json.load(open(path_to_prompt, "r", encoding="utf-8"))


    # Prompts
    template_extractor_prompt =f"""
        Eres un experto en extraer datos estructurados de documentos no estructurados.
        
        # Seguiras el siguiente workflow
        1. (Mandatorio): Consulta la base de datos vectorial para extraer la información.
        2. La información extraida la estructuraras como un texto en lenguaje natural.
        3. Regresa el texto con la información. 

        # Si no encontraste la información, expresa en el texto, que dicha información no fue encontrada.

        # El cliente valora mas la "precisión" que la rapidez, así que tómate tu tiempo para validar cada campo.
        
        Información a encontrar:
        {prompt_template_dict}
    """

    template_validator_prompt =f"""
        Eres un experto en extraer datos estructurados de documentos no estructurados.

        # Contexto: 
        Ayudaras a extraer información a partir de un texto con la información,
        con la informaicón que encuentres del texto, llenaras los campos que
        se te soliciten (structure outputs). 

        Es importante que si no encuentras la información en el texto para un campo, 
        llenes dicho campo con un `None` 
        

        Texto con la información: 
    """


    print("Extract information (querying to vector).")
    vector_database = "vs_691f65fce4748191b8d0772f546b616f" # Personal database

    llm = ChatOpenAI(model="gpt-4.1-2025-04-14").bind_tools([
         {
            "type": "file_search", "vector_store_ids": 
            [
                vector_database
            ]
        }
    ])


    # print("Prompt for extrating the information to be sent: ", template_extractor_prompt)

    extractor_agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=template_extractor_prompt
    )

    result_validation = extractor_agent.invoke({
        "messages": [
            {
                "type": "user",
                "content": "Extrae la información que se te solicita."
            }
        ],
        # "files": [
        #     # "file-8Bb2EngLyndDwnqGy7bhU4"
        #     "file-G1ULKc6JuLN1fRFLtkv6a1"
        # ]
    })

    messages = result_validation.get('messages')

    # print("TRAVERSING THE MESSAGES +++++++++++++++++++++++++++++++++")
    # for message in messages:
    #     print(message.content)
    # print("END OF TRAVERSING THE MESSAGES +++++++++++++++++++++++++++++++++")

    print("Text with the information")
    print(messages[len(messages) - 1].content[1])

    print("Struct information.")



    # return
    template_validator_prompt += f"{messages[len(messages) - 1].content[1]}"



    recognaizer_agent = create_agent(
        model=llm,
        tools=[],
        response_format=ProviderStrategy(GeneralInvoiceInformation),
        system_prompt=template_validator_prompt
    )


    result_validation = recognaizer_agent.invoke({
        "messages": [
            {
                "type": "user",
                "content": "Extrae la información que se te solicita"
            }
        ]
    })
    model_output = result_validation.get('structured_response')


    
    
    
    # Use the actual model output from result_validation
    json_path = "D:\\DOCUMENTS\\self_study\\Agents\\langchain_learning\\automatic_program_engineering\\desired_output\\output_auto_qualitas.json"
    with open(json_path, "r", encoding="utf-8") as f:
        reference_output = json.load(f)


    if model_output:
        model_output_dict = model_output.dict() if hasattr(model_output, 'dict') else model_output
    else:
        print("No structured_response found in result_validation.")
        model_output_dict = {}

    # Compare each field
    comparison = {}
    for key in reference_output:
        ref_val = reference_output[key]
        model_val = model_output_dict.get(key, None)
        comparison[key] = {
            "expected": ref_val,
            "actual": model_val,
            "match": ref_val == model_val
        }

    print("\nField-by-field comparison:")
    for k, v in comparison.items():
        print(f"{k}: expected={v['expected']} | actual={v['actual']} | match={v['match']}")

    total = len(comparison)
    correct = sum(1 for v in comparison.values() if v["match"])
    accuracy = correct / total if total > 0 else 0.0
    print(f"\nOverall accuracy: {accuracy*100:.2f}% ({correct}/{total} fields correct)")


execute_test()