from pydantic import BaseModel
from typing import List, Optional

class TransactionInfo(BaseModel):
    wallet_id: str
    transaction_details: dict

class Message(BaseModel):
    recipient_id: str
    content: str
