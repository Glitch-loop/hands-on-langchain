from pydantic import BaseModel, Field

class BlueprintSchema(BaseModel):
    poliza: str|None = Field(default=None, description="")
    inicioPeriodoVigencia: str|None = Field(default=None, description="")
    finalPeriodoVigencia: str|None = Field(default=None, description="")
    aseguradora: str|None = Field(default=None, description="")
