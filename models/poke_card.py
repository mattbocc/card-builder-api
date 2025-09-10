from pydantic import BaseModel
from typing import Optional


class Poke(BaseModel):
    name: str
    type: str
    stage: int
    portrait: bool
    special_event: Optional[str] = None
    additional_prompt: Optional[str] = None
