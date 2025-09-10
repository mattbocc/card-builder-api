from fastapi import APIRouter
import logging
from models.poke_card import Poke

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/poke")


@router.put("/card")
def create_card(Poke):
    return "placeholder!"
