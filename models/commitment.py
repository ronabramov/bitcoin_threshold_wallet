from pydantic import BaseModel
from models.algorithm_step import Algorithm_Step
from phe import PaillierPublicKey

class Commitment(BaseModel):
    algorith_step : Algorithm_Step
    commiting_user_index : int
    commited_values : list[int]
    paillier_public_key : PaillierPublicKey