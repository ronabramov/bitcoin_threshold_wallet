from pydantic import BaseModel
from models.DTOs.transaction_dto import TransactionDTO
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from models.models import wallet_key_generation_share, user_public_share, WalletGenerationMessage, GPowerX
from models.value_knowledge_zk_proof import value_knowledge_zk_proof
from models.commitment import Commitment
from models.protocols.MtaAndMtaWcMessages import MtaChallenge, MtaCommitmentAlice, MtaCommitmentBob, MtaProofForChallengeAlice, MtaProofForChallengeBob, MtaWcCommitmentBob
from typing import Optional, Union
from models.DTOs.MessageType import MessageType

class MessageDTO(BaseModel):
    """
    A Wrapper for messages - adding the functionality of type
    The Wallet Listener would parse every message w.r.t it's type.
    """
    type: MessageType
    data: Union[TransactionDTO, TransactionResponseDTO, wallet_key_generation_share, user_public_share,GPowerX,
                Commitment, value_knowledge_zk_proof, MtaChallenge, MtaCommitmentAlice,
                  MtaCommitmentBob, MtaProofForChallengeAlice, MtaProofForChallengeBob, MtaWcCommitmentBob, WalletGenerationMessage]
    sender_id: Optional[str] = None  # Matrix ID of the sender
    wallet_id: Optional[str] = None  # ID of the wallet this message relates to
    transaction_id: Optional[str] = None  # ID of the transaction if applicable
    user_index: Optional[int] = None  # Index of the user in the wallet