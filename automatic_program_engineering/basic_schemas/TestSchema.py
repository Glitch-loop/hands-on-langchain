from pydantic import BaseModel, Field

class TestSchema(BaseModel):
    example: str = Field(description="This is an example field.")
