
import os
def create_new_schema(fields_in_schema: list[str], class_name: str) -> str:
	"""
	Generates a Pydantic BaseModel with the given fields (all as str with empty description)
	and writes it to a Python file named after the class_name in the same directory.
	"""
	# Sanitize class and file names
	safe_class = ''.join(x for x in class_name if x.isalnum())
	safe_file = f"{safe_class}.py"
	lines = [
		"from pydantic import BaseModel, Field",
		f"class {safe_class}(BaseModel):\n"
	]
	for field in fields_in_schema:
		safe_field = field.strip().replace(' ', '_')
		lines.append(f"    {safe_field}: str = Field(description='')\n")

	model_code = ''.join(lines)

	def write_schema_to(output_dir=None):
		if output_dir is None:
			output_dir = os.path.join(os.path.dirname(__file__), "..", "basic_schemas")
		os.makedirs(output_dir, exist_ok=True)
		out_path = os.path.join(output_dir, safe_file)
		with open(out_path, "w", encoding="utf-8") as f:
			f.write(model_code)
		return out_path

	# For backward compatibility, write to default location and return path
	return write_schema_to


def add_descriptions_to_schema(file_path: str, field_descriptions: dict[str, str]) -> None:
	"""
	Adds descriptions to the fields in the given Pydantic BaseModel file.
	Modifies the file in place. Handles relative paths robustly.
	"""
	
	# If file_path is not absolute, resolve relative to the current working directory
	if not os.path.isabs(file_path):
		file_path = os.path.abspath(file_path)

	with open(file_path, "r", encoding="utf-8") as f:
		lines = f.readlines()

	for i, line in enumerate(lines):
		for field, description in field_descriptions.items():
			if line.strip().startswith(f"{field}: str = Field("):
				lines[i] = f"    {field}: str = Field(description='{description}')\n"

	with open(file_path, "w", encoding="utf-8") as f:
		f.writelines(lines)


# Example usage:
# A new file named 'TestSchema' will be created in the 'basic_schemas' directory with the specified field.
# create_new_schema(['example'], 'TestSchema')


# Add descriptions to the previously created schema
add_descriptions_to_schema(
	'D:\\DOCUMENTS\\self_study\\Agents\\langchain_learning\\automatic_program_engineering\\basic_schemas\\GeneralInvoiceInformation.py',
	{
    "poliza": "Plantilla de prompt:Extrae el número de póliza del texto. Busca etiquetas como: 'PÓLIZA', 'No. de póliza', 'PÓLIZA No.', 'PÓLIZA:'. Prioriza el valor del encabezado o del bloque de identificación de la póliza. Devuelve solo el número sin texto adicional ni espacios. Si hay varias pólizas, devuelve la correspondiente al vehículo descrito en el documento. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo de formato): 1290415403",
    "inicioPeriodoVigencia": "Plantilla de prompt:Extrae la fecha de inicio de vigencia de la póliza. Busca frases como: 'Vigencia del … al …', 'Inicio de vigencia', 'Desde', 'Vigencia: del'. Si aparece el rango 'del X al Y', toma X como inicio. Convierte la fecha a timestamp Unix en segundos a las 00:00:00 hora America/Mexico_City. Acepta formatos dd/mm/aaaa, dd-mm-aaaa, y con mes en texto. Devuelve solo el número. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 1666545600",
    "finalPeriodoVigencia": "Plantilla de prompt:Extrae la fecha de fin de vigencia de la póliza. Busca frases como: 'Vigencia del … al …', 'Fin de vigencia', 'Hasta', 'Vigente hasta'. Si aparece el rango 'del X al Y', toma Y como fin. Convierte la fecha a timestamp Unix en segundos a las 00:00:00 hora America/Mexico_City. Devuelve solo el número. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 1698081600",
    "aseguradora": "Plantilla de prompt:Identifica el nombre de la aseguradora emisora. Busca en encabezado, logotipo y razón social: 'QUÁLITAS', 'Quálitas Compañía de Seguros, S.A. de C.V.', 'Qualitas'. Normaliza a 'QUÁLITAS'. Devuelve solo el nombre normalizado. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (normalizado): QUÁLITAS",
    "ramo": "Plantilla de prompt:Extrae el ramo del seguro. Busca etiquetas como: 'Ramo', 'Línea de negocio'. En pólizas de auto suele ser 'Automóviles' o 'Autos'. Si no hay etiqueta explícita pero aparece información vehicular (VIN/NIV de 17 caracteres, placas, modelo), establece 'Automóviles'. Devuelve solo el valor del ramo. Si no procede, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): Automóviles",
    "subRamo": "Plantilla de prompt:Extrae el subramo o uso. Busca etiquetas como: 'Subramo', 'Uso', 'Tipo de uso', 'Residente/Turista', 'Particular/Servicio Público'. Devuelve el texto tal como aparece, en mayúsculas. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplos): Particular, Residente",
    "cobertura": "Plantilla de prompt:Extrae el plan/paquete de cobertura contratada. Busca etiquetas: 'Cobertura', 'Paquete', 'Plan', con valores típicos 'Amplia', 'Limitada', 'Responsabilidad Civil', 'RC'. Si hay varias menciones, toma la que esté junto a la identificación del vehículo o del contrato. Devuelve solo el nombre de la cobertura. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): Amplia",
    "formaDePago": "Plantilla de prompt:Extrae la forma de pago. Busca etiquetas: 'Forma de pago', 'Plan de pagos', 'Modalidad de pago'. Normaliza a uno de: CONTADO, MENSUAL, BIMESTRAL, TRIMESTRAL, SEMESTRAL, ANUAL, FINANCIADO. Si se menciona una tarjeta o banco pero no la periodicidad, usa CONTADO si se observa un único pago total. Devuelve solo el valor normalizado. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (normalizado): CONTADO",
    "primaNeta": "Plantilla de prompt:Extrae el importe de Prima Neta. Busca etiquetas: 'Prima Neta', 'Subtotal prima'. Elige el monto del desglose de primas, no el total. Normaliza eliminando símbolo de moneda y espacios; conserva signo si existe y dos decimales con punto. Devuelve solo el número como texto. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 11557.97",
    "primerPago": "Plantilla de prompt:Extrae el monto del Primer Pago. Busca etiquetas: 'Primer pago', 'Primer pago con inscripción' o similar. Si la forma de pago es CONTADO, el Primer Pago suele ser igual al Total. Normaliza eliminando símbolo de moneda y separadores de miles; dos decimales con punto. Devuelve solo el número como texto. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 13777.10",
    "pagoPosterior": "Plantilla de prompt:Extrae el monto de Pago(s) Posterior(es). Busca etiquetas: 'Pagos posteriores', 'Pago(s) posterior(es)', 'Pagos subsecuentes'. Si la forma de pago es CONTADO, devuelve 0. Si aparecen varios pagos posteriores, devuelve el importe unitario por pago, no la suma. Normaliza a número con dos decimales y punto. Devuelve solo el número como texto o 0 si no aplica.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 0",
    "descuento": "Plantilla de prompt:Extrae el total de Descuento(s) aplicados. Busca etiquetas: 'Descuento', 'Bonificación', 'Promoción' en el desglose. Si hay múltiples descuentos, suma sus importes. Normaliza a número con dos decimales, punto decimal y sin símbolo de moneda. Si no hay descuento, devuelve 0. Devuelve solo el número como texto.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 0.00",
    "iva": "Plantilla de prompt:Extrae el IVA del desglose de primas. Busca etiquetas: 'IVA', 'Impuesto al Valor Agregado' y toma el monto (no el porcentaje). Normaliza a número con dos decimales y punto. Devuelve solo el número como texto. Si no aplica, devuelve 0.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 1900.29",
    "tasaFinanciamiento": "Plantilla de prompt:Extrae el importe monetario por financiamiento (recargo o descuento). Busca etiquetas: 'Tasa de financiamiento', 'Recargo por financiamiento', 'Intereses por financiamiento' en el desglose económico. Si aparece también un porcentaje, devuelve el monto en dinero, conservando el signo si es descuento (negativo). Normaliza a número con dos decimales y punto. Si no aplica, devuelve 0.\nEntrada: {{texto_documento}}\nSalida esperada (formato): -231.16",
    "derechoPoliza": "Plantilla de prompt:Extrae el importe de Derecho de Póliza (gastos de expedición). Busca etiquetas: 'Derecho de póliza', 'Gastos de expedición'. Normaliza a número con dos decimales, punto decimal. Devuelve solo el número como texto. Si no aparece, devuelve 0.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 0.00",
    "total": "Plantilla de prompt:Extrae el Total a pagar de la póliza. Busca etiquetas: 'Total', 'Total a pagar', 'Prima total' y toma el gran total del recibo o desglose. Normaliza a número con dos decimales y punto. Devuelve solo el número como texto. Si hay varios totales (por pagos parciales), elige el total del periodo actual contratado.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 13777.10",
    "cargoPorFinanciamiento": "Plantilla de prompt:Extrae el Cargo por Financiamiento si se presenta como línea separada del desglose. Busca etiquetas: 'Cargo por financiamiento', 'Recargo por financiamiento'. Prioriza el monto monetario, no el porcentaje. Normaliza a número con dos decimales y punto. Si no existe o ya está reflejado en otra línea, devuelve 0.\nEntrada: {{texto_documento}}\nSalida esperada (formato): 0.00",
    "rfcAsegurado": "Plantilla de prompt:Extrae el RFC del Asegurado. Busca en secciones: 'Datos del asegurado' o 'Contratante' con etiqueta 'RFC'. Prioriza el RFC del Asegurado; si no existe, usa el del Contratante. Valida formato mexicano de 12 o 13 caracteres alfanuméricos (con homoclave). Devuelve en mayúsculas sin espacios. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): ROME4605046U9",
    "nombreAsegurado": "Plantilla de prompt:Extrae el nombre del Asegurado. Busca etiquetas: 'Asegurado', 'Nombre del asegurado'. Si no aparece, usa el 'Contratante'. Evita capturar el nombre del agente o beneficiario. Devuelve el nombre completo tal como aparece, en mayúsculas si así está. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): ELENA ROMERO MEDINA",
    "numeroSerie": "Plantilla de prompt:Extrae el Número de Serie del vehículo (VIN/NIV). Busca etiquetas: 'Número de serie', 'No. de serie', 'VIN', 'NIV'. Debe ser un identificador alfanumérico de 17 caracteres. Devuelve en mayúsculas, sin espacios. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): 3N1CN7AD1HK409639",
    "modelo": "Plantilla de prompt:Extrae el modelo/año del vehículo. Busca etiquetas: 'Modelo', 'Año modelo', 'Año' junto con el vehículo. Devuelve cuatro dígitos (aaaa). Si hay varios años (fabricación/modelo), elige el 'Modelo'. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): 2017",
    "numeroPlacas": "Plantilla de prompt:Extrae el número de placas del vehículo. Busca etiquetas: 'Placas', 'No. de placa(s)'. Devuelve el texto alfanumérico en mayúsculas, sin espacios adicionales. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): JNC8318",
    "adaptaciones": "Plantilla de prompt:Extrae las Adaptaciones o Equipo Especial del vehículo si existen. Busca etiquetas: 'Adaptaciones', 'Equipo especial'. Si aparece 'N/A', 'No aplica' o está en blanco, devuelve vacío. Devuelve el texto tal como aparece (hasta 100 caracteres). Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): ",
    "version": "Plantilla de prompt:Extrae la Versión o Clave de versión del vehículo. Busca etiquetas: 'Versión', 'Clave versión', 'Vers.'. Puede ser un código numérico o alfanumérico. Devuelve el valor sin etiquetas. Si no se encuentra, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): 02134",
    "beneficiarioPreferente": "Plantilla de prompt:Extrae el Beneficiario Preferente o Acreedor Prendario. Busca etiquetas: 'Beneficiario preferente', 'Acreedor prendario', 'Beneficiario' en la sección de datos financieros del vehículo. Devuelve el nombre de la institución si existe. Si no aplica o está vacío, devuelve vacío.\nEntrada: {{texto_documento}}\nSalida esperada (ejemplo): "
  }
)