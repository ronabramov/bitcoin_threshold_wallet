from typing import List, Optional
from pydantic import BaseModel

class new_transaction_request(BaseModel):
    wallet_id: str
    creating_user_id : str
    amount_of_money : int
    title : str
    description : str
    accepting_users: List[str]

    