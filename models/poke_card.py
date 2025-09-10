from pydantic import BaseModel
from typing import Optional


class Poke(BaseModel):
    name: str
    card_type: str
    stage: int
    portrait: bool
    special_event: Optional[str]
    additional_prompt: Optional[str]
