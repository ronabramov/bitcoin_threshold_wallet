from pydantic import BaseModel, ConfigDict
from phe import paillier, EncryptedNumber
from ecdsa.ellipticcurve import PointJacobi

class MtaChallenge(BaseModel):
    """Used both by Alice and Bob."""
    challenge: int

    def to_dict(self):
        return {"challenge": self.challenge}

    @classmethod
    def from_dict(cls, data):
        return cls(challenge=data["challenge"])

class MtaCommitmentAlice(BaseModel):
    """First Message in Mta Protocol, sent from Alice To Bob."""
    c_A: EncryptedNumber
    z: int
    z_prime: int
    t: int
    v: int
    w: int
    model_config = ConfigDict(arbitrary_types_allowed=True) 

    def to_dict(self):
        return {
            "c_A": (self.c_A.ciphertext, self.c_A.exponent),  # Serialize EncryptedNumber
            "z": self.z,
            "z_prime": self.z_prime,
            "t": self.t,
            "v": self.v,
            "w": self.w
        }

    @classmethod
    def from_dict(cls, data, paillier_public_key):
        return cls(
            c_A=EncryptedNumber(paillier_public_key, data["c_A"][0], data["c_A"][1]),  # Restore EncryptedNumber
            z=data["z"],
            z_prime=data["z_prime"],
            t=data["t"],
            v=data["v"],
            w=data["w"]
        )

class MtaProoveForChallengeAlice(BaseModel):
    """Third message in Mta Protocol, sent from Alice."""
    s: int
    s_1: int
    s_2: int
    t_1: int
    t_2: int
    model_config = ConfigDict(arbitrary_types_allowed=True) 
    def to_dict(self):
        return {
            "s": self.s,
            "s_1": self.s_1,
            "s_2": self.s_2,
            "t_1": self.t_1,
            "t_2": self.t_2
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class MtaCommitmentBob(BaseModel):
    """First Message in Bob Response of Mta Protocol."""
    c_B: EncryptedNumber
    z: int
    z_prime: int
    t: int
    v: int
    w: int
    model_config = ConfigDict(arbitrary_types_allowed=True) 
    def to_dict(self):
        return {
            "c_B": (self.c_B.ciphertext, self.c_B.exponent),  # Serialize EncryptedNumber
            "z": self.z,
            "z_prime": self.z_prime,
            "t": self.t,
            "v": self.v,
            "w": self.w
        }

    @classmethod
    def from_dict(cls, data, paillier_public_key):
        return cls(
            c_B=EncryptedNumber(paillier_public_key, data["c_B"][0], data["c_B"][1]),  # Restore EncryptedNumber
            z=data["z"],
            z_prime=data["z_prime"],
            t=data["t"],
            v=data["v"],
            w=data["w"]
        )

class MtaProoveForChallengeBob(BaseModel):
    """Third message in Bob response of Mta Protocol."""
    s: int
    s_1: int
    s_2: int
    t_1: int
    t_2: int
    model_config = ConfigDict(arbitrary_types_allowed=True) 
    def to_dict(self):
        return {
            "s": self.s,
            "s_1": self.s_1,
            "s_2": self.s_2,
            "t_1": self.t_1,
            "t_2": self.t_2
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class MtaWcCommitmentBob(MtaCommitmentBob):
    """Extended Commitment from Bob in Mta Protocol including an Elliptic Curve Point."""
    u: PointJacobi
    
    def to_dict(self):
        base_data = super().to_dict()
        base_data["u"] = {"x": self.u.x(), "y": self.u.y(), "z": self.u.z()}
        return base_data

    @classmethod
    def from_dict(cls, data, paillier_public_key):
        base_obj = super().from_dict(data, paillier_public_key)
        point = PointJacobi(None, data["u"]["x"], data["u"]["y"], data["u"]["z"])  # Restore PointJacobi
        return cls(**base_obj.dict(), u=point)
