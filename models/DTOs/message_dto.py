from pydantic import BaseModel
from models.DTOs.transaction_dto import TransactionDTO
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from models.models import wallet_key_generation_share, user_public_share, WalletGenerationMessage
from models.value_knowledge_zk_proof import value_knowledge_zk_proof
from models.commitment import Commitment
from models.protocols.MtaAndMtaWcMessages import MtaChallenge, MtaCommitmentAlice, MtaCommitmentBob, MtaProofForChallengeAlice, MtaProofForChallengeBob, MtaWcCommitmentBob
from typing import Union
from models.DTOs.MessageType import MessageType

class MessageDTO(BaseModel):
    """
    A Wrapper for messages - adding the functionality of type
    The Wallet Listener would parse every message w.r.t it's type.
    """
    type: MessageType
    data: Union[TransactionDTO, TransactionResponseDTO, wallet_key_generation_share, user_public_share,
                Commitment, value_knowledge_zk_proof, MtaChallenge, MtaCommitmentAlice,
                  MtaCommitmentBob, MtaProofForChallengeAlice, MtaProofForChallengeBob, MtaWcCommitmentBob, WalletGenerationMessage]