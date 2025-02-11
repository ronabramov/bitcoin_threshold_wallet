from pydantic import BaseModel
from transaction_dto import TransactionDTO
from typing import Union

class MessageDTO(BaseModel):
    """
    A Wrapper for messages - adding the functionality of type
    The Wallet Listener would parse every message w.r.t it's type.
    """
    type: str
    data: Union[TransactionDTO]