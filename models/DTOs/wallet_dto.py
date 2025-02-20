from pydantic import BaseModel
from typing import Optional


class WalletDto(BaseModel):
    wallet_id : str
    threshold : int
    users : Optional[str] #@alice:matrix.org,@bob:matrix.org - we will save comma parsed absolute path for participating users
    n : int #Number of users.
