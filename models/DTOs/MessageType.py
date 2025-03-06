from enum import Enum

class MessageType(Enum):
    TransactionRequest = "transaction_request" # propose new transaction
    TransactionResponse = "transaction_response" # approve transacion
    KeyGenerationShare = "key_generation_share"  # this is a private message between users
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
    GPowerX = "g_power_x"