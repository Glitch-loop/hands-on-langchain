from pydantic import BaseModel, Field
import json

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.structured_output import ProviderStrategy
import base64

template_validator_prompt =f"""
    Eres un experto en extraer datos estructurados de documentos no estructurados.

    # Utiliza la base de datos vectorial y el archivo adjuntado en el mensaje del usuario para encontrar la información que se te solicita.

    # El cliente valora mas la "precisión" que la rapidez, así que tómate tu tiempo para validar cada campo.
    """

prompt_template_dict = {
    "poliza": "Extrae el número de póliza principal del documento de QUÁLITAS. Busca etiquetas como: \"Póliza\", \"Póliza No.\", \"No. de póliza\", \"Núm. de póliza\". Reglas: 1) Prioriza el número ubicado en el encabezado o cerca del logo/razón social de QUÁLITAS. 2) Excluye números de endoso, cotización o siniestro. 3) Devuelve solo dígitos sin espacios ni guiones. 4) Si hay varios, toma el de mayor prominencia o el que esté junto a la palabra Póliza. Si no existe, devuelve cadena vacía.",
    "inicioPeriodoVigencia": "Extrae la fecha de inicio de vigencia. Busca patrones: \"Vigencia: Desde ___ Hasta ___\", \"Inicio de vigencia\", \"Desde\". Acepta formatos comunes: dd/mm/aaaa, dd-mm-aaaa, dd de mmm de aaaa. Convierte la fecha a Unix epoch en segundos a las 00:00:00 hora local (CDMX). Devuelve solo el entero en texto (sin separadores ni etiquetas). Si no existe, devuelve cadena vacía.",
    "finalPeriodoVigencia": "Extrae la fecha de fin de vigencia. Busca patrones: \"Vigencia: Desde ___ Hasta ___\", \"Fin de vigencia\", \"Hasta\". Acepta formatos comunes: dd/mm/aaaa, dd-mm-aaaa, dd de mmm de aaaa. Convierte la fecha a Unix epoch en segundos a las 23:59:59 hora local (CDMX). Devuelve solo el entero en texto (sin separadores ni etiquetas). Si no existe, devuelve cadena vacía.",
    "aseguradora": "Extrae el nombre de la aseguradora emisora. En documentos de esta clase debe ser \"QUÁLITAS\" o su razón social completa (por ejemplo, \"QUÁLITAS Compañía de Seguros, S.A. de C.V.\"). Devuelve la marca corta \"QUÁLITAS\" si aparece; si no, devuelve el nombre tal como esté impreso. Sin etiquetas adicionales. Si no existe, cadena vacía.",
    "ramo": "Extrae el ramo (por ejemplo: Autos, Daños, Vida). Busca etiquetas: \"Ramo\", \"Ramo/Producto\". Devuelve el texto tal como aparece, en mayúsculas si ya viene así. Si no se especifica, devuelve cadena vacía.",
    "subRamo": "Extrae el subramo o producto/plan específico. Busca: \"Subramo\", \"Producto\", \"Plan\". Devuelve el texto exacto sin etiquetas. Si no existe, cadena vacía.",
    "cobertura": "Extrae la cobertura/paquete principal (ej.: Amplia, Limitada, RC). Busca: \"Cobertura\", \"Paquete\". Prefiere el valor indicado en el resumen de la póliza. Devuelve solo el nombre de la cobertura. Si no existe, cadena vacía.",
    "formaDePago": "Extrae la forma o plan de pago. Busca: \"Forma de pago\", \"Plan de pagos\", \"Modalidad de pago\". Valores típicos: CONTADO, MENSUAL, SEMESTRAL, ANUAL, TARJETA, TRANSFERENCIA. Devuelve el valor textual exactamente como aparece (sin etiquetas). Si no existe, cadena vacía.",
    "primaNeta": "Extrae el importe de \"Prima Neta\". Busca la etiqueta exacta \"Prima Neta\". Devuelve solo el número en formato 12345.67 (punto decimal, sin símbolo $, sin espacios, con separadores de miles opcionales removidos). Si no existe, cadena vacía.",
    "primerPago": "Extrae el importe de \"Primer pago\" o \"Pago inicial\". Busca: \"Primer pago\", \"Pago inicial\". Devuelve número en formato 12345.67 (sin $ ni comas de miles). Si no existe, cadena vacía.",
    "pagoPosterior": "Extrae el importe de \"Pago(s) posterior(es)\" o \"Pagos subsecuentes\". Busca: \"Pago(s) posterior(es)\", \"Pagos subsecuentes\", \"Pago(s) siguientes\". Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, devuelve 0 si el plan es CONTADO; de lo contrario, cadena vacía.",
    "descuento": "Extrae el importe de \"Descuento\" o \"Bonificación\" si se muestra en el desglose. Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, devuelve 0.",
    "iva": "Extrae el IVA del desglose. Busca: \"IVA\" o \"I.V.A.\" asociado a importes. Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, cadena vacía.",
    "tasaFinanciamiento": "Extrae el monto asociado a financiamiento/bonificación por financiamiento. Busca etiquetas como: \"Tasa de financiamiento\", \"Costo/ cargo por financiamiento\", \"Bonificación por pago de contado\". Si aparece como monto negativo, conserva el signo. Devuelve número en formato 12345.67 (sin $ ni comas). Si solo hay porcentaje y no monto, devuelve el porcentaje con el signo % (por ejemplo, 10%). Si no existe, cadena vacía.",
    "derechoPoliza": "Extrae \"Derecho(s) de póliza\". Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, devuelve 0.",
    "total": "Extrae el \"Total\" o \"Total a pagar\" del resumen de cobro. Prioriza el total final tras impuestos, derechos y cargos. Devuelve número en formato 12345.67 (sin $ ni comas). Si no existe, cadena vacía.",
    "cargoPorFinanciamiento": "Extrae el \"Cargo por financiamiento\" (si se separa explícitamente del total). Devuelve número en formato 12345.67 (sin $ ni comas, conserva signo si es negativo). Si no existe, devuelve 0.",
    "rfcAsegurado": "Extrae el RFC del Asegurado (no del Agente ni de la Aseguradora). Busca cerca de \"Asegurado\" o \"Contratante\". Valida con patrón: [A-Z&Ñ]{3,4}\\d{6}[A-Z0-9]{2,3}. Devuelve en mayúsculas sin espacios. Si hay dos (contratante y asegurado), prioriza el de Asegurado. Si no existe, cadena vacía.",
    "nombreAsegurado": "Extrae el nombre completo del Asegurado. Busca: \"Asegurado:\", \"Nombre del asegurado\". Si aparecen Contratante y Asegurado, devuelve el de Asegurado. Respeta mayúsculas/acentos tal como en el documento. Devuelve solo el nombre sin etiquetas. Si no existe, cadena vacía.",
    "numeroSerie": "Extrae el número de serie/VIN del vehículo. Busca: \"No. de serie\", \"Núm. de serie\", \"VIN\". Valida longitud 17 con A-Z y 0-9 (excluye I, O, Q si es posible). Devuelve en mayúsculas sin espacios. Si no existe, cadena vacía.",
    "modelo": "Extrae el año modelo del vehículo. Busca: \"Modelo\" o \"Año\" cercano a los datos del vehículo. Devuelve un número de cuatro dígitos (por ejemplo, 2017). Si no existe, cadena vacía.",
    "numeroPlacas": "Extrae el número de placas. Busca: \"Placas\", \"No. de placas\". Devuelve en mayúsculas, sin espacios adicionales. Si no existe, cadena vacía.",
    "adaptaciones": "Extrae el campo de \"Adaptaciones y conversiones\" o \"Adaptaciones\" si aparece como texto/descripción. Si solo se reporta un monto sin descripción, devuelve ese texto/monto; si no hay adaptaciones declaradas, devuelve cadena vacía.",
    "version": "Extrae la versión o clave vehicular. Busca: \"Versión\", \"Clave versión\", \"Clave vehicular\", \"Código\" cercano a datos del vehículo. Devuelve exactamente el código/texto mostrado (por ejemplo, 02134). Si no existe, cadena vacía.",
    "beneficiarioPreferente": "Extrae el Beneficiario/Acreedor preferente (por ejemplo, una institución financiera). Busca: \"Beneficiario preferente\", \"Acreedor preferente\". Si hay varios, devuelve el primero principal. Devuelve solo el nombre de la entidad. Si no existe, cadena vacía."
  }

def safe_description(val):
    # Ensure the description is a string and escape problematic quotes
    if not isinstance(val, str):
        val = str(val)
    return val.replace('"', "'")

class GeneralInvoiceInformation(BaseModel):
    poliza: str = Field(default="", description="Plantilla de prompt: Extrae el número de póliza del texto. Busca etiquetas como: PÓLIZA, No. de póliza, PÓLIZA No., PÓLIZA:. Prioriza el valor del encabezado o del bloque de identificación de la póliza. Devuelve solo el número sin texto adicional ni espacios. Si hay varias pólizas, devuelve la correspondiente al vehículo descrito en el documento. Si no se encuentra, devuelve vacío.")
    inicioPeriodoVigencia: str = Field(default="", description="Plantilla de prompt: Extrae la fecha de inicio de vigencia de la póliza. Busca frases como: Vigencia del... al..., Inicio de vigencia, Desde, Vigencia: del. Si aparece el rango del X al Y, toma X como inicio. Convierte la fecha a timestamp Unix en segundos a las 00:00:00 hora America/Mexico_City. Acepta formatos dd/mm/aaaa, dd-mm-aaaa, y con mes en texto. Devuelve solo el número. Si no se encuentra, devuelve vacío. ")
    finalPeriodoVigencia: str = Field(default="", description="Plantilla de prompt: Extrae la fecha de fin de vigencia de la póliza. Busca frases como: Vigencia del... al..., Fin de vigencia, Hasta, Vigente hasta. Si aparece el rango del X al Y, toma Y como fin. Convierte la fecha a timestamp Unix en segundos a las 00:00:00 hora America/Mexico_City. Devuelve solo el número. Si no se encuentra, devuelve vacío. ")
    aseguradora: str = Field(default="", description="Plantilla de prompt: Identifica el nombre de la aseguradora emisora. Busca en encabezado, logotipo y razón social: QUÁLITAS, Quálitas Compañía de Seguros, S.A. de C.V., Qualitas. Normaliza a QUÁLITAS. Devuelve solo el nombre normalizado. Si no se encuentra, devuelve vacío.")
    ramo: str = Field(default="", description="Plantilla de prompt: Extrae el ramo del seguro. Busca etiquetas como: Ramo, Línea de negocio. En pólizas de auto suele ser Automóviles o Autos. Si no hay etiqueta explícita pero aparece información vehicular (VIN/NIV de 17 caracteres, placas, modelo), establece Automóviles. Devuelve solo el valor del ramo. Si no procede, devuelve vacío.")
    subRamo: str = Field(default="", description="Plantilla de prompt: Extrae el subramo o uso. Busca etiquetas como: Subramo, Uso, Tipo de uso, Residente/Turista, Particular/Servicio Público. Devuelve el texto tal como aparece, en mayúsculas. Si no se encuentra, devuelve vacío.")
    cobertura: str = Field(default="", description="Plantilla de prompt: Extrae el plan/paquete de cobertura contratada. Busca etiquetas: Cobertura, Paquete, Plan, con valores típicos Amplia, Limitada, Responsabilidad Civil, RC. Si hay varias menciones, toma la que esté junto a la identificación del vehículo o del contrato. Devuelve solo el nombre de la cobertura. Si no se encuentra, devuelve vacío.")
    formaDePago: str = Field(default="", description="Plantilla de prompt: Extrae la forma de pago. Busca etiquetas: Forma de pago, Plan de pagos, Modalidad de pago. Normaliza a uno de: CONTADO, MENSUAL, BIMESTRAL, TRIMESTRAL, SEMESTRAL, ANUAL, FINANCIADO. Si se menciona una tarjeta o banco pero no la periodicidad, usa CONTADO si se observa un único pago total. Devuelve solo el valor normalizado. Si no se encuentra, devuelve vacío.")
    primaNeta: str = Field(default="", description="Plantilla de prompt: Extrae el importe de Prima Neta. Busca etiquetas: Prima Neta, Subtotal prima. Elige el monto del desglose de primas, no el total. Normaliza eliminando símbolo de moneda y espacios; conserva signo si existe y dos decimales con punto. Devuelve solo el número como texto. Si no se encuentra, devuelve vacío. ")
    primerPago: str = Field(default="", description="Plantilla de prompt: Extrae el monto del Primer Pago. Busca etiquetas: Primer pago, Primer pago con inscripción o similar. Si la forma de pago es CONTADO, el Primer Pago suele ser igual al Total. Normaliza eliminando símbolo de moneda y separadores de miles; dos decimales con punto. Devuelve solo el número como texto. Si no se encuentra, devuelve vacío. ")
    pagoPosterior: str = Field(default="", description="Plantilla de prompt: Extrae el monto de Pago(s) Posterior(es). Busca etiquetas: Pagos posteriores, Pago(s) posterior(es), Pagos subsecuentes. Si la forma de pago es CONTADO, devuelve 0. Si aparecen varios pagos posteriores, devuelve el importe unitario por pago, no la suma. Normaliza a número con dos decimales y punto. Devuelve solo el número como texto o 0 si no aplica. ")
    descuento: str = Field(default="", description="Plantilla de prompt: Extrae el total de Descuento(s) aplicados. Busca etiquetas: Descuento, Bonificación, Promoción en el desglose. Si hay múltiples descuentos, suma sus importes. Normaliza a número con dos decimales, punto decimal y sin símbolo de moneda. Si no hay descuento, devuelve 0. Devuelve solo el número como texto. ")
    iva: str = Field(default="", description="Plantilla de prompt: Extrae el IVA del desglose de primas. Busca etiquetas: IVA, Impuesto al Valor Agregado y toma el monto (no el porcentaje). Normaliza a número con dos decimales y punto. Devuelve solo el número como texto. Si no aplica, devuelve 0. ")
    tasaFinanciamiento: str = Field(default="", description="Plantilla de prompt: Extrae el importe monetario por financiamiento (recargo o descuento). Busca etiquetas: Tasa de financiamiento, Recargo por financiamiento, Intereses por financiamiento en el desglose económico. Si aparece también un porcentaje, devuelve el monto en dinero, conservando el signo si es descuento (negativo). Normaliza a número con dos decimales y punto. Si no aplica, devuelve 0. ")
    derechoPoliza: str = Field(default="", description="Plantilla de prompt: Extrae el importe de Derecho de Póliza (gastos de expedición). Busca etiquetas: Derecho de póliza, Gastos de expedición. Normaliza a número con dos decimales, punto decimal. Devuelve solo el número como texto. Si no aparece, devuelve 0. ")
    total: str = Field(default="", description="Plantilla de prompt: Extrae el Total a pagar de la póliza. Busca etiquetas: Total, Total a pagar, Prima total y toma el gran total del recibo o desglose. Normaliza a número con dos decimales y punto. Devuelve solo el número como texto. Si hay varios totales (por pagos parciales), elige el total del periodo actual contratado. ")
    cargoPorFinanciamiento: str = Field(default="", description="Plantilla de prompt: Extrae el Cargo por Financiamiento si se presenta como línea separada del desglose. Busca etiquetas: Cargo por financiamiento, Recargo por financiamiento. Prioriza el monto monetario, no el porcentaje. Normaliza a número con dos decimales y punto. Si no existe o ya está reflejado en otra línea, devuelve 0. ")
    rfcAsegurado: str = Field(default="", description="Plantilla de prompt: Extrae el RFC del Asegurado. Busca en secciones: Datos del asegurado o Contratante con etiqueta RFC. Prioriza el RFC del Asegurado; si no existe, usa el del Contratante. Valida formato mexicano de 12 o 13 caracteres alfanuméricos (con homoclave). Devuelve en mayúsculas sin espacios. Si no se encuentra, devuelve vacío.")
    nombreAsegurado: str = Field(default="", description="Plantilla de prompt: Extrae el nombre del Asegurado. Busca etiquetas: Asegurado, Nombre del asegurado. Si no aparece, usa el Contratante. Evita capturar el nombre del agente o beneficiario. Devuelve el nombre completo tal como aparece, en mayúsculas si así está. Si no se encuentra, devuelve vacío.")
    numeroSerie: str = Field(default="", description="Plantilla de prompt: Extrae el Número de Serie del vehículo (VIN/NIV). Busca etiquetas: Número de serie, No. de serie, VIN, NIV. Debe ser un identificador alfanumérico de 17 caracteres. Devuelve en mayúsculas, sin espacios. Si no se encuentra, devuelve vacío.")
    modelo: str = Field(default="", description="Plantilla de prompt: Extrae el modelo/año del vehículo. Busca etiquetas: Modelo, Año modelo, Año junto con el vehículo. Devuelve cuatro dígitos (aaaa). Si hay varios años (fabricación/modelo), elige el Modelo. Si no se encuentra, devuelve vacío.")
    numeroPlacas: str = Field(default="", description="Plantilla de prompt: Extrae el número de placas del vehículo. Busca etiquetas: Placas, No. de placa(s). Devuelve el texto alfanumérico en mayúsculas, sin espacios adicionales. Si no se encuentra, devuelve vacío.")
    adaptaciones: str = Field(default="", description="Plantilla de prompt: Extrae las Adaptaciones o Equipo Especial del vehículo si existen. Busca etiquetas: Adaptaciones, Equipo especial. Si aparece N/A, No aplica o está en blanco, devuelve vacío. Devuelve el texto tal como aparece (hasta 100 caracteres). Si no se encuentra, devuelve vacío.")
    version: str = Field(default="", description="Plantilla de prompt: Extrae la Versión o Clave de versión del vehículo. Busca etiquetas: Versión, Clave versión, Vers. Puede ser un código numérico o alfanumérico. Devuelve el valor sin etiquetas. Si no se encuentra, devuelve vacío.")
    beneficiarioPreferente: str = Field(default="", description="Plantilla de prompt: Extrae el Beneficiario Preferente o Acreedor Prendario. Busca etiquetas: Beneficiario preferente, Acreedor prendario, Beneficiario en la sección de datos financieros del vehículo. Devuelve el nombre de la institución si existe. Si no aplica o está vacío, devuelve vacío.")

def execute_test():
    # gpt-5 is not the best for extracting information.
    vector_database = "vs_691f5a8294bc8191b0d872bf3d4c2cfb" # Personal database

    # gpt-5.1-2025-11-13 - 32%
    # gpt-4.1-2025-04-14 - 52.00% 
    llm = ChatOpenAI(model="gpt-4.1-2025-04-14").bind_tools([
         {
            "type": "file_search", "vector_store_ids": 
            [
                vector_database
            ]
        }
    ])

    agent_template_validator = create_agent(
        model=llm,
        tools=[],
        response_format=ProviderStrategy(GeneralInvoiceInformation),
        system_prompt=template_validator_prompt
    )

    # with open("D:\\DOCUMENTS\\self_study\\Agents\\langchain_learning\\automatic_program_engineering\\input_files\\polizas prueba\\Auto Qualitas.pdf", "rb") as f:
    #     encoded = base64.b64encode(f.read()).decode("utf-8")

    result_validation = agent_template_validator.invoke({
        "messages": [
            {
                "type": "user",
                "content": "Extrae la información que se te solicita usando la base de datos vectorial y el archivo adjunto."
            }
        ],
        "files": [
            "file-8Qz9RuWugdi3gqLMXh54pz"
        ]
    })

    print("Result from validation agent: ", result_validation)
    # Use the actual model output from result_validation
    json_path = "D:\\DOCUMENTS\\self_study\\Agents\\langchain_learning\\automatic_program_engineering\\desired_output\\output_auto_qualitas.json"
    with open(json_path, "r", encoding="utf-8") as f:
        reference_output = json.load(f)

    print(result_validation.get('structured_response'))
    model_output = result_validation.get('structured_response')
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