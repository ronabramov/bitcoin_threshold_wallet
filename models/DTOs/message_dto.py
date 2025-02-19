from pydantic import BaseModel
from models.DTOs.transaction_dto import TransactionDTO
from models.transaction_response import TransactionResponse
from models.models import key_generation_share, user_public_share, WalletGenerationMessage
from models.value_knowledge_zk_proof import value_knowledge_zk_proof
from models.commitment import Commitment
from models.protocols.MtaAndMtaWcMessages import MtaChallenge, MtaCommitmentAlice, MtaCommitmentBob, MtaProofForChallengeAlice, MtaProofForChallengeBob, MtaWcCommitmentBob
from typing import Union
from enum import Enum

class MessageType(Enum):
    Transaction = "transaction"
    TransactionRequest = "transaction_request"
    TransactionResponse = "transaction_response"
    KeyGenerationShare = "key_generation_share"
    UserPublicShare = "user_public_share"
    Commitment = "commitment"
    ValueKnowledgeZkProof = "value_knowledge_zk_proof"
    MtaChallenge = "mta_challenge"
    MtaCommitmentAlice = "mta_commitment_alice"
    MtaCommitmentBob = "mta_commitment_bob"
    MtaProofForChallengeAlice = "mta_proof_for_challenge_alice"
    MtaProofForChallengeBob = "mta_proof_for_challenge_bob"
    MtaWcCommitmentBob = "mta_wc_commitment_bob"
    WalletGenerationMessage = "wallet_generation_message"


class MessageDTO(BaseModel):
    """
    A Wrapper for messages - adding the functionality of type
    The Wallet Listener would parse every message w.r.t it's type.
    """
    type: MessageType
    data: Union[TransactionDTO, TransactionResponse, key_generation_share, user_public_share,
                Commitment, value_knowledge_zk_proof, MtaChallenge, MtaCommitmentAlice,
                  MtaCommitmentBob, MtaProofForChallengeAlice, MtaProofForChallengeBob, MtaWcCommitmentBob, WalletGenerationMessage]