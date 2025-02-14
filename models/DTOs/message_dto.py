from pydantic import BaseModel
from DTOs.transaction_dto import TransactionDTO
from models.transaction_response import TransactionResponse
from models.models import user_key_generation_share, user_public_share
from models.value_knowledge_zk_proof import value_knowledge_zk_proof
from models.commitment import Commitment
from models.protocols.MtaAndMtaWcMessages import MtaChallenge, MtaCommitmentAlice, MtaCommitmentBob, MtaProoveForChallengeAlice, MtaProoveForChallengeBob, MtaWcCommitmentBob
from typing import Union

class MessageDTO(BaseModel):
    """
    A Wrapper for messages - adding the functionality of type
    The Wallet Listener would parse every message w.r.t it's type.
    """
    type: str
    data: Union[TransactionDTO, TransactionResponse, user_key_generation_share, user_public_share,
                Commitment, value_knowledge_zk_proof, MtaChallenge, MtaCommitmentAlice,
                  MtaCommitmentBob, MtaProoveForChallengeAlice, MtaProoveForChallengeBob, MtaWcCommitmentBob]