from pydantic import BaseModel, validator

class Click2call(BaseModel):         
    src:  int
    dst:  int
    context:  str


   