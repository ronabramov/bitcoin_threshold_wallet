from pydantic import BaseModel
from models.transaction_dto import TransactionDTO
from models.transaction_response import TransactionResponse
from models.models import user_key_generation_share
from typing import Union

class MessageDTO(BaseModel):
    """
    A Wrapper for messages - adding the functionality of type
    The Wallet Listener would parse every message w.r.t it's type.
    """
    type: str
    data: Union[TransactionDTO, TransactionResponse, user_key_generation_share]