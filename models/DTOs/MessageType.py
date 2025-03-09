from enum import Enum

class MessageType(Enum):
    """
    Enumeration of all message types used in the threshold wallet system.
    This includes messages for wallet generation, transaction handling,
    and the MTA protocol for threshold ECDSA.
    """
    # Wallet and Transaction Management
    TransactionRequest = "TransactionRequest"
    TransactionResponse = "TransactionResponse"
    UserPublicShare = "UserPublicShare"
    KeyGenerationShare = "KeyGenerationShare"
    Commitment = "Commitment"
    WalletGenerationMessage = "WalletGenerationMessage"
    GPowerX = "GPowerX"
    
    # Basic Value Knowledge ZK Proof
    ValueKnowledgeZkProof = "ValueKnowledgeZkProof"
    
    # MTA Protocol (Alice Role)
    MtaCommitmentAlice = "MtaCommitmentAlice"        # Alice sends commitment of 'a'
    MtaProofForChallengeAlice = "MtaProofForChallengeAlice" # Alice's proof for Bob's challenge
    MtaChallenge = "MtaChallenge"              # Alice's challenge to Bob
    
    # MTA Protocol (Bob Role)
    MtaCommitmentBob = "MtaCommitmentBob"          # Bob sends commitment and encrypted result
    MtaProofForChallengeBob = "MtaProofForChallengeBob"   # Bob's proof for Alice's challenge
    
    # MtAwc Protocol (with check - for secret key)
    MtaWcCommitmentAlice = "MtaWcCommitmentAlice"      # Alice sends commitment with check
    MtaWcProofForChallengeAlice = "MtaWcProofForChallengeAlice"  # Alice's proof for MtaWc challenge
    MtaWcChallenge = "MtaWcChallenge"            # Alice's challenge for MtaWc
    MtaWcCommitmentBob = "MtaWcCommitmentBob"        # Bob's response for MtaWc
    MtaWcProofForChallengeBob = "MtaWcProofForChallengeBob" # Bob's proof for MtaWc challenge