from pydantic import BaseModel
from typing import Optional


class Poke(BaseModel):
    image_name: str
    type: str
    stage: str
    portrait: bool
    special_event: Optional[str] = None
    additional_prompt: Optional[str] = None
