from unittest import result
from pydantic import BaseModel, Field
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.agents.middleware import FilesystemFileSearchMiddleware
import uuid
import json
import base64
import os

# Define prompt for automatic program engineering (APE).
template_generator_prompt = """
    Eres un experto prompt engineer especializado en extraer datos estructurados de documentos no estructurados.

    Recibirás como entrada:
        - El archivo del cual se extraerá la información.
        - La información deseada en el esquema de salida.

    Instrucciónes:
    1. Analiza los campos de la salida estructurada.
    2. En el JSON que se te proporciona, localiza el output del campo correspondiente.
    3. Una vez localizado, encuentra en que parte del documento está esa información.
    4. Genera una plantilla de prompt detallada para cada campo, enfocándote en patrones y diseño del documento.
    5. Evita dar ejemplos de salidas en la descripción.
"""

"""
    Eres un experto en extraer datos estructurados de documentos no estructurados.

    Recibirás como entrada:
    - El archivo del cual se extraerá la información.
    - La información deseada en el esquema de salida.

    # Tu tarea es generar una plantilla de prompt para cada campo de la salida estructurada.

    > Enfócate mas en los patrones y diseño del documento mas que en obtener los valores específicos.
    > Esta descripción será de mucha ayuda para que en proximas llamadas sepas donde esta "localizada" la información correctamente.

    Tomate tu tiempo para dar una descripción detallada para cada campo en el esquema de salida.

    # Evita dar ejemplo de salidas en la descripción.
"""


template_validator_prompt =f"""
    Eres un experto en extraer datos estructurados de documentos no estructurados.
    Recibirás como entrada:
    - El archivo del cual se extraerá la información.
    - La información deseada en el esquema de salida.
"""

json_desired_output = "D:\\DOCUMENTS\\self_study\\Agents\\langchain_learning\\automatic_program_engineering\\desired_output\\output_auto_chubb.json"

# Define the data model to create the prompts.
class GeneralInvoiceInformation(BaseModel):
    poliza: str                 = Field(default="")
    inicioPeriodoVigencia: str   = Field(default="")
    finalPeriodoVigencia: str    = Field(default="")
    # aseguradora: str            = Field(default="")
    # ramo: str                   = Field(default="")
    # subRamo: str                = Field(default="")
    # cobertura: str              = Field(description="")
    # formaDePago: str           = Field(default="")
    # primaNeta: str             = Field(default="")
    # primerPago: str            = Field(default="")
    # pagoPosterior: str     = Field(default="")
    # descuento: str         = Field(default="")
    # iva: str               = Field(default="")
    # tasaFinanciamiento: str = Field(default="")
    # derechoPoliza: str     = Field(default="")
    # total: str             = Field(default="")
    # cargoPorFinanciamiento: str = Field(default="")
    # rfcAsegurado: str     = Field(default="")
    # nombreAsegurado: str  = Field(default="")
    # numeroSerie: str      = Field(default="")
    # modelo: str           = Field(default="")
    # numeroPlacas: str     = Field(default="")
    # adaptaciones: str     = Field(default="")
    # version: str          = Field(default="")
    # beneficiarioPreferente: str = Field(default="")

# Auxiliar functions
def safe_description(val):
    # Ensure the description is a string and escape problematic quotes
    if not isinstance(val, str):
        val = str(val)
    return val.replace('"', "'")

class LangChainMessage(BaseModel):
    role: str
    content: str

# Sub-processes 
def auto_generate_prompt(messages: list[LangChainMessage]) -> dict:
    prompt_template_dict = {}

    # Selecting the model
    llm = ChatOpenAI(
        model="gpt-5.1-2025-11-13",
    )

    # Create agent 
    agent_template_generator = create_agent(
        model=llm,
        tools=[],
        response_format=ProviderStrategy(GeneralInvoiceInformation),
        middleware=[
            FilesystemFileSearchMiddleware(
                root_path="automatic_program_engineering/input_files/first_test/"
                # max_files=1,
            )
        ],
        system_prompt=template_generator_prompt,
    )

    # Desired output data. 
    with open(json_desired_output, "r", encoding="utf-8") as f:
        desired_output = json.load(f)


    # Invoke agent to get prompt template.
    messages.append(
        LangChainMessage(
            role="developer",
            content=f"""
                Aquí está la información en output_auto_chubb.json
                {desired_output}
            """
        )
    )

    result = agent_template_generator.invoke(
        {
            "messages": [
                {
                    "type": "developer",
                    "content": f"""
                        Aquí está la información en output_auto_chubb.json
                        {desired_output}
                    """
                }
            ]
        }
    )

    prompt_template = result.get("structured_response")
    

    # If you want it as a dictionary:
    if prompt_template:
        prompt_template_dict = prompt_template.dict()
    else:
        print("No structured_response found in result.")

    return prompt_template_dict
    
def extract_information_from_prompt(prompt_template_dict: dict) -> dict:
    # Selecting the model
    llm = ChatOpenAI(
        model="gpt-4.1",
    )

    class GeneralInvoiceInformationModified(BaseModel):
        poliza: str                 = Field(default="", description=safe_description(prompt_template_dict.get("poliza", "")))
        inicioPeriodoVigencia: str  = Field(default="", description=safe_description(prompt_template_dict.get("inicioPeriodoVigencia", "")))
        finalPeriodoVigencia: str   = Field(default="", description=safe_description(prompt_template_dict.get("finalPeriodoVigencia", "")))
        aseguradora: str            = Field(default="", description=safe_description(prompt_template_dict.get("aseguradora", "")))
        ramo: str                   = Field(default="", description=safe_description(prompt_template_dict.get("ramo", "")))
        subRamo: str                = Field(default="", description=safe_description(prompt_template_dict.get("subRamo", "")))
        cobertura: str              = Field(default="", description=safe_description(prompt_template_dict.get("cobertura", "")))
        formaDePago: str            = Field(default="", description=safe_description(prompt_template_dict.get("formaDePago", "")))
        primaNeta: str              = Field(default="", description=safe_description(prompt_template_dict.get("primaNeta", "")))
        primerPago: str             = Field(default="", description=safe_description(prompt_template_dict.get("primerPago", "")))
        pagoPosterior: str          = Field(default="", description=safe_description(prompt_template_dict.get("pagoPosterior", "")))
        descuento: str              = Field(default="", description=safe_description(prompt_template_dict.get("descuento", "")))
        iva: str                    = Field(default="", description=safe_description(prompt_template_dict.get("iva", "")))
        tasaFinanciamiento: str     = Field(default="", description=safe_description(prompt_template_dict.get("tasaFinanciamiento", "")))
        derechoPoliza: str          = Field(default="", description=safe_description(prompt_template_dict.get("derechoPoliza", "")))
        total: str                  = Field(default="", description=safe_description(prompt_template_dict.get("total", "")))
        cargoPorFinanciamiento: str = Field(default="", description=safe_description(prompt_template_dict.get("cargoPorFinanciamiento", "")))
        rfcAsegurado: str           = Field(default="", description=safe_description(prompt_template_dict.get("rfcAsegurado", "")))
        nombreAsegurado: str        = Field(default="", description=safe_description(prompt_template_dict.get("nombreAsegurado", "")))
        numeroSerie: str            = Field(default="", description=safe_description(prompt_template_dict.get("numeroSerie", "")))
        modelo: str                 = Field(default="", description=safe_description(prompt_template_dict.get("modelo", "")))
        numeroPlacas: str           = Field(default="", description=safe_description(prompt_template_dict.get("numeroPlacas", "")))
        adaptaciones: str           = Field(default="", description=safe_description(prompt_template_dict.get("adaptaciones", "")))
        version: str                = Field(default="", description=safe_description(prompt_template_dict.get("version", "")))
        beneficiarioPreferente: str = Field(default="", description=safe_description(prompt_template_dict.get("beneficiarioPreferente", "")))

    agent_template_validator = create_agent(
        model=llm,
        tools=[],
        response_format=ProviderStrategy(GeneralInvoiceInformationModified),
        middleware=[
            FilesystemFileSearchMiddleware(
                root_path="automatic_program_engineering/input_files/first_test/"
                # max_files=1,
            )
        ],
        system_prompt=template_validator_prompt,
    )

    result_validation = agent_template_validator.invoke({
        "messages": [
            {
                "type": "developer",
                "content": f"""
                    Extrae la información de acuerdo con tu prompt.
                """
            }
        ]
    })

    model_output = result_validation.get('structured_response')

    if model_output:
        model_output_dict = model_output.dict() if hasattr(model_output, 'dict') else model_output
    else:
        print("No structured_response found in result_validation.")
        model_output_dict = {}
    
    return model_output_dict

def assess_the_extraction_accuracy(information_extracted: dict, reference_output: dict) -> dict:
    # Compare each field
    comparison = {}

    for key in reference_output:
        ref_val = reference_output[key]
        model_val = information_extracted.get(key, None)
        comparison[key] = {
            "expected": ref_val,
            "actual": model_val,
            "match": ref_val == model_val
        }

    print("\nField-by-field comparison:")
    for k, v in comparison.items():
        print(f"{k}: expected={v['expected']} | actual={v['actual']} | match={v['match']}")

    # Calculate accuracy
    total = len(comparison)
    correct = sum(1 for v in comparison.values() if v["match"])
    accuracy = correct / total if total > 0 else 0.0
    print(f"\nOverall accuracy: {accuracy*100:.2f}%")
    
    comparison['overall_accuracy'] = accuracy

    return comparison

def store_prompt_template(prompt_template_dict: dict, accuracy: dict) -> str:
    prompt_template_dir = "automatic_program_engineering/prompt_template"
    os.makedirs(prompt_template_dir, exist_ok=True)

    # Save template dict and accuracy
    prompt_template_to_store = {
        "prompt_template": prompt_template_dict,
        "accuracy": accuracy
    }

    unique_id = str(uuid.uuid4())
    prompt_template_path = os.path.join(prompt_template_dir, f"prompt_template_{unique_id}.json")
    with open(prompt_template_path, "w", encoding="utf-8") as f:
        json.dump(prompt_template_to_store, f, ensure_ascii=False, indent=2)
    print(f"\nPrompt template and accuracy saved to {prompt_template_path}")

# Main process
def execute_ape_process():
    messages:list[LangChainMessage] = []

    for i in range(3):
        print(f"Starting iteration {i + 1}...\n")

        print("Starting Automatic Program Engineering (APE) process...\n")
        prompt_template_dict = auto_generate_prompt(messages)

        print("Using the auto prompt template to extract information.\n")
        information_extracted = extract_information_from_prompt(prompt_template_dict)

        # Use the actual model output from result_validation
        with open(json_desired_output, "r", encoding="utf-8") as f:
            reference_output = json.load(f)

        print("Assess accuracy of the template.\n")
        comparision = assess_the_extraction_accuracy(information_extracted, reference_output)
        
        messages.append(
            LangChainMessage(
                role="system",
                content=f"Iteración pasada: {comparision}"
            )
        )


        store_prompt_template(prompt_template_dict, comparision["overall_accuracy"])

execute_ape_process()