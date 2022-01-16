from pydantic import BaseModel, validator

class Click2call(BaseModel):         
    src:  int
    dst:  int
    context:  str
    
    @validator('context')
    def context_format(cls, context):        
        if context.startswith("from-"):
            return context
        else:
            raise ValueError('Invalid context name')

   