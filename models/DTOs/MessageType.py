from enum import Enum

class MessageType(Enum):
    # RON - i keep forgetting what is the difference between transaction request and transaction response v-v
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
