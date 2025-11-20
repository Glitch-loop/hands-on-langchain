from pydantic import BaseModel, Field
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.agents.middleware import FilesystemFileSearchMiddleware
import uuid
import json
import base64


# Define prompt for automatic program engineering (APE).
template_generator_prompt = """
    Eres un experto en extraer datos estructurados de documentos no estructurados.

    Recibirás como entrada:
    - El archivo del cual se extraerá la información.
    - La información deseada en el esquema de salida.

    Tu tarea es generar una plantilla de prompt para cada campo del JSON.

    > Usa el archivo para reconocer patrones y contexto que ayuden a extraer la información requerida y
    usa la información deseada para saber qué información extraer.
"""

json_desired_output = "D:\\DOCUMENTS\\self_study\\Agents\\langchain_learning\\automatic_program_engineering\\desired_output\\output_auto_qualitas.json"

# Define the data model to create the prompts.
class GeneralInvoiceInformation(BaseModel):
    poliza: str                 = Field(default="", description="")
    inicioPeriodoVigencia: str   = Field(default="")
    finalPeriodoVigencia: str    = Field(default="")
    aseguradora: str            = Field(default="")
    ramo: str                   = Field(default="")
    subRamo: str                = Field(default="")
    cobertura: str              = Field(description="")
    formaDePago: str           = Field(default="")
    primaNeta: str             = Field(default="")
    primerPago: str            = Field(default="")
    pagoPosterior: str     = Field(default="")
    descuento: str         = Field(default="")
    iva: str               = Field(default="")
    tasaFinanciamiento: str = Field(default="")
    derechoPoliza: str     = Field(default="")
    total: str             = Field(default="")
    cargoPorFinanciamiento: str = Field(default="")
    rfcAsegurado: str     = Field(default="")
    nombreAsegurado: str  = Field(default="")
    numeroSerie: str      = Field(default="")
    modelo: str           = Field(default="")
    numeroPlacas: str     = Field(default="")
    adaptaciones: str     = Field(default="")
    version: str          = Field(default="")
    beneficiarioPreferente: str = Field(default="")
    
    

# class VehicleInvoiceInformation(BaseModel): 

def execute_ape_proccess():
    # Selecting the model
    llm = ChatOpenAI(
        model="gpt-5",
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

    # Extracting the desired output data. 
    with open(json_desired_output, "r", encoding="utf-8") as f:
        desired_output = json.load(f)

    # Get prompt template.
    result = agent_template_generator.invoke(
        {
            "messages": [
                {
                    "type": "developer",
                    "content": f"""
                        Aquí está la información en output_auto_qualitas.json
                        {desired_output}
                    """
                }
            ]
        }
    )

    prompt_template = result.get("structured_response")
    prompt_template_dict = {}
    # If you want it as a dictionary:
    if prompt_template:
        prompt_template_dict = prompt_template.dict()
        # print(prompt_template_dict)
    else:
        print("No structured_response found in result.")

    # Test prompt template.
    template_validator_prompt =f"""
    Eres un experto en extraer datos estructurados de documentos no estructurados.
    Recibirás como entrada:
    - El archivo del cual se extraerá la información.
    - La información deseada en el esquema de salida.
    """
    # Por favor, extrae la información de acuerdo con la siguiente plantilla de prompt:
    # {prompt_template_dict}


    def safe_description(val):
        # Ensure the description is a string and escape problematic quotes
        if not isinstance(val, str):
            val = str(val)
        return val.replace('"', "'")

    class GeneralInvoiceInformationModified(BaseModel):
        poliza: str             = Field(default="", description=safe_description(prompt_template_dict.get("poliza", "")))
        inicioPeriodoVigencia: str    = Field(default="", description=safe_description(prompt_template_dict.get("inicioPeriodoVigencia", "")))
        finalPeriodoVigencia: str    = Field(default="", description=safe_description(prompt_template_dict.get("finalPeriodoVigencia", "")))
        aseguradora: str        = Field(default="", description=safe_description(prompt_template_dict.get("aseguradora", "")))
        ramo: str               = Field(default="", description=safe_description(prompt_template_dict.get("ramo", "")))
        subRamo: str            = Field(default="", description=safe_description(prompt_template_dict.get("subRamo", "")))
        cobertura: str          = Field(default="", description=safe_description(prompt_template_dict.get("cobertura", "")))
        formaDePago: str       = Field(default="", description=safe_description(prompt_template_dict.get("formaDePago", "")))
        primaNeta: str         = Field(default="", description=safe_description(prompt_template_dict.get("primaNeta", "")))
        primerPago: str        = Field(default="", description=safe_description(prompt_template_dict.get("primerPago", "")))
        pagoPosterior: str     = Field(default="", description=safe_description(prompt_template_dict.get("pagoPosterior", "")))
        descuento: str         = Field(default="", description=safe_description(prompt_template_dict.get("descuento", "")))
        iva: str               = Field(default="", description=safe_description(prompt_template_dict.get("iva", "")))
        tasaFinanciamiento: str = Field(default="", description=safe_description(prompt_template_dict.get("tasaFinanciamiento", "")))
        derechoPoliza: str     = Field(default="", description=safe_description(prompt_template_dict.get("derechoPoliza", "")))
        total: str             = Field(default="", description=safe_description(prompt_template_dict.get("total", "")))
        cargoPorFinanciamiento: str = Field(default="", description=safe_description(prompt_template_dict.get("cargoPorFinanciamiento", "")))
        rfcAsegurado: str     = Field(default="", description=safe_description(prompt_template_dict.get("rfcAsegurado", "")))
        nombreAsegurado: str  = Field(default="", description=safe_description(prompt_template_dict.get("nombreAsegurado", "")))
        numeroSerie: str      = Field(default="", description=safe_description(prompt_template_dict.get("numeroSerie", "")))
        modelo: str           = Field(default="", description=safe_description(prompt_template_dict.get("modelo", "")))
        numeroPlacas: str     = Field(default="", description=safe_description(prompt_template_dict.get("numeroPlacas", "")))
        adaptaciones: str     = Field(default="", description=safe_description(prompt_template_dict.get("adaptaciones", "")))
        version: str          = Field(default="", description=safe_description(prompt_template_dict.get("version", "")))
        beneficiarioPreferente: str = Field(default="", description=safe_description(prompt_template_dict.get("beneficiarioPreferente", "")))

    print(template_validator_prompt)
    print("+++++++++++++++++++++++++++++++++++++++")
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

    # Calculate result

    # Example: Simulate agent validator output (replace with actual call)
    # validator_result = agent_template_validator.invoke(...)
    # model_output = validator_result['structured_response']
    # If model_output is a Pydantic model, convert to dict
    # model_output_dict = model_output.dict() if hasattr(model_output, 'dict') else model_output


    # Use the actual model output from result_validation
    with open(json_path, "r", encoding="utf-8") as f:
        reference_output = json.load(f)

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

    # Store prompt template.

    # Store prompt template and accuracy
    import os
    prompt_template_dir = "automatic_program_engineering/prompt_template"
    os.makedirs(prompt_template_dir, exist_ok=True)
    unique_id = str(uuid.uuid4())
    prompt_template_path = os.path.join(prompt_template_dir, f"prompt_template_{unique_id}.json")

    # Calculate accuracy
    total = len(comparison)
    correct = sum(1 for v in comparison.values() if v["match"])
    accuracy = correct / total if total > 0 else 0.0

    # Save template dict and accuracy
    to_store = {
        "prompt_template": prompt_template_dict,
        "accuracy": accuracy
    }
    with open(prompt_template_path, "w", encoding="utf-8") as f:
        json.dump(to_store, f, ensure_ascii=False, indent=2)
    print(f"\nPrompt template and accuracy saved to {prompt_template_path}")

execute_ape_process()