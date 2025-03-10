from enum import Enum

class MessageType(Enum):
    """
    Enumeration of all message types used in the threshold wallet system.
    This includes messages for wallet generation, transaction handling,
    and the MTA protocol for threshold ECDSA.
    Each message type clearly indicates whether it's sent by Alice or Bob.
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
    MtaAliceCommitment = "MtaAliceCommitment"        # Alice sends commitment of 'a'
    MtaAliceProofForChallenge = "MtaAliceProofForChallenge" # Alice's proof for Bob's challenge
    MtaAliceChallengeToBob = "MtaAliceChallengeToBob"  # Alice's challenge to Bob
    
    # MTA Protocol (Bob Role)
    MtaBobChallengeToAlice = "MtaBobChallengeToAlice"  # Bob's challenge to Alice
    MtaBobCommitment = "MtaBobCommitment"           # Bob sends commitment and encrypted result
    MtaBobProofForChallenge = "MtaBobProofForChallenge"  # Bob's proof for Alice's challenge
    
    # MtAwc Protocol with check - for secret key (Alice Role)
    MtaWcAliceCommitment = "MtaWcAliceCommitment"      # Alice sends commitment with check
    MtaWcAliceProofForChallenge = "MtaWcAliceProofForChallenge"  # Alice's proof for MtaWc challenge
    MtaWcAliceChallengeToBob = "MtaWcAliceChallengeToBob"  # Alice's challenge to Bob for MtaWc
    
    # MtAwc Protocol with check - for secret key (Bob Role)
    MtaWcBobChallengeToAlice = "MtaWcBobChallengeToAlice"  # Bob's challenge to Alice for MtaWc
    MtaWcBobCommitment = "MtaWcBobCommitment"        # Bob's response for MtaWc
    MtaWcBobProofForChallenge = "MtaWcBobProofForChallenge" # Bob's proof for MtaWc challenge