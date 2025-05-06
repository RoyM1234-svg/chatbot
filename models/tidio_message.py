import pydantic
from pydantic.alias_generators import to_camel

class TidioMessage(pydantic.BaseModel):
    device: str
    message: str
    message_id: str
    project_public_key: str
    visitor_id: str
    url: str
    
    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel
    }