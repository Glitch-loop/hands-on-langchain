from pydantic import BaseModel, Field

class BlueprintSchema(BaseModel):
    primaNeta: str|None = Field(default=None, description="")
    primerPago: str|None = Field(default=None, description="")
    pagoPosterior: str|None = Field(default=None, description="")
    descuento: str|None = Field(default=None, description="")
    iva: str|None = Field(default=None, description="")
    tasaFinanciamiento: str|None = Field(default=None, description="")
    derechoPoliza: str|None = Field(default=None, description="")
    total: str|None = Field(default=None, description="")
