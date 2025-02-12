from pydantic import BaseModel
from phe import paillier, EncryptedNumber
from ecdsa.ellipticcurve import PointJacobi

class MtaChallenge(BaseModel):
    """
    Used both by Alice and Bob
    """
    challenge : int 


class MtaCommitmentAlice(BaseModel):
    """
    First Message in Mta Protocol, sent from Alice To Bob
    """
    c_A : EncryptedNumber
    z : int
    z_prime : int
    t : int
    v : int
    w : int

class MtaProoveForChallengeAlice(BaseModel):
    """
    Third message in MtaProtocl, sent from Alice.
    """
    s : int
    s_1 : int
    s_2 : int
    t_1 : int
    t_2 : int

class MtaCommitmentBob(BaseModel):
    """
    First Message in Bob Response of Mta Protocol
    """
    c_B : EncryptedNumber
    z : int
    z_prime : int
    t : int
    v : int
    w : int

class MtaProoveForChallengeBob(BaseModel):
    """
    Third message in Bob response of MtaProtocl
    """
    s : int
    s_1 : int
    s_2 : int
    t_1 : int
    t_2 : int


class MtaWcCommitmentBob(MtaCommitmentBob):
    u : PointJacobi