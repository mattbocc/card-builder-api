from pydantic import BaseModel
from typing import List


class Order(BaseModel):
    esty_order_id: str
