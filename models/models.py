from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from ecdsa.ellipticcurve import PointJacobi, CurveFp
from ecdsa.curves import Curve, SECP256k1
from ecdsa import curves
from phe import paillier


class TransactionInfo(BaseModel):
    wallet_id: str
    transaction_details: dict

class Message(BaseModel):
    recipient_id: str
    content: str

class WalletGenerationMessage(BaseModel):
    threshold : int
    max_number_of_participants : int
    curve_name : str

    def get_type():
        return "wallet_generation_message"

class user_modulus(BaseModel):
    N : int
    h1 : int
    h2: int 

class user_key_generation_share(BaseModel):
    """
    Consider p as the polynomial generated by the user produced this share.
    target_user_evaluation : evaulated polynomial at target user index
    v_i = g^ai - where ai is the coefficient of the shamir polynomial generated by generating user
    v_0 - g^secret
    This share can be tested for validness through Feldaman_VSS_Protocl.Verify_Share method.
    curve : The curved used for the generation.
    """
    transaction_id : str
    generating_user_index : str
    target_user_matrix_id : str # Will be filled right before sending message. 
    target_user_index : int
    target_user_evaluation : int
    v_i : List[PointJacobi]
    v_0 : PointJacobi
    curve : str

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allows custom types - For Point Jacobi property

    def to_dict(self):
        curve_instance = self.v_0.curve()
        curve_data = {
            "p": curve_instance.p(),
            "a": curve_instance.a(),
            "b": curve_instance.b(),
            "order": curve_instance.order(),
            "name": self.curve
        }

        return {
            "transaction_id": self.transaction_id,
            "generating_user_index": self.generating_user_index,
            "target_user_matrix_id": self.target_user_matrix_id,
            "target_user_index": self.target_user_index,
            "target_user_evaluation": self.target_user_evaluation,
            "v_i": [{"x": p.x(), "y": p.y(), "z": p.z()} for p in self.v_i],  # List of points
            "v_0": {"x": self.v_0.x(), "y": self.v_0.y(), "z": self.v_0.z()},  # Single point
            "curve": curve_data
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize and reconstruct elliptic curve points inside the object."""
        curve_data = data["curve"]
        # Reconstruct the curve
        curve_instance = CurveFp(
            curve_data["p"],
            curve_data["a"],
            curve_data["b"],
            curve_data["order"],
            name=curve_data["name"]
        )

        # Reconstruct v_0
        v_0_data = data["v_0"]
        v_0 = PointJacobi(curve_instance, v_0_data["x"], v_0_data["y"], v_0_data["z"])

        # Reconstruct v_i (list of points)
        v_i = [
            PointJacobi(curve_instance, p["x"], p["y"], p["z"])
            for p in data["v_i"]
        ]

        return cls(
            transaction_id=data["transaction_id"],
            generating_user_index=data["generating_user_index"],
            target_user_matrix_id=data["target_user_matrix_id"],
            target_user_index=data["target_user_index"],
            target_user_evaluation=data["target_user_evaluation"],
            v_i=v_i,
            v_0=v_0,
            curve=curve_data["name"]
        )


    def get_type():
        return f"user_key_generation_share"

class user_public_share(BaseModel):
    user_index: int
    user_id: str
    paillier_public_key: paillier.PaillierPublicKey
    user_modulus: user_modulus

    model_config = ConfigDict(arbitrary_types_allowed=True) 

    def to_dict(self):
        return {
            "user_index": self.user_index,
            "user_id": self.user_id,
            "paillier_public_key": {"n": self.paillier_public_key.n},  # Store only `n`
            "user_modulus": {
                "N": self.user_modulus.N,
                "h1": self.user_modulus.h1,
                "h2": self.user_modulus.h2
            }
        }

    @classmethod
    def from_dict(cls, data):
        paillier_pub = paillier.PaillierPublicKey(n=data["paillier_public_key"]["n"])
        user_mod = user_modulus(
            N=data["user_modulus"]["N"],
            h1=data["user_modulus"]["h1"],
            h2=data["user_modulus"]["h2"]
        )
        return cls(
            user_index=data["user_index"],
            user_id=data["user_id"],
            paillier_public_key=paillier_pub,
            user_modulus=user_mod,
        )

    def get_type():
        return "user_public_share"
    
class generating_user_public_share(user_public_share):
    curve_name : str
    def to_dict(self):
        base_data = super().to_dict()
        base_data["curve_name"] = self.curve_name
        return base_data

    @classmethod
    def from_dict(cls, data):
        public_data = user_public_share.from_dict(data)
        curve_name = data["curve_name"]
        
        return cls(
            user_index=public_data.user_index,
            user_id=public_data.user_id,
            paillier_public_key=public_data.paillier_public_key,
            user_modulus=public_data.user_modulus,
            curve_name=curve_name
        )
    def get_type():
        return "generating_user_public_share"
   

class user_secret_signature_share(BaseModel):
    """
    Includes user secrets - MUSTN'T BE BROADCASTED OR SHARED
    Denote by P = sum_j p_j , where p_j are the generated polynomial by the jth player.
    The Shamir share of the secret key of the Signature x = sum_j u_j is given by
    P(user_index) =  sum_j p_j(user_index)       --- x = P(0)
    The share a user should posses along the signature algorithm
    Composed from shares of all other users participated in the transaction
    user_evaluation - the user secret key. 
    """
    threshold: int
    user_index: int
    user_id: str
    user_evaluation: int
    group: curves.Curve
    paillier_public_key: paillier.PaillierPublicKey
    paillier_secret_key: paillier.PaillierPrivateKey
    user_modulus: user_modulus
    num_of_updates: int = 0
    original_secret_share: Optional[int] = None
    shrinked_secret_share: Optional[int] = None
    model_config = ConfigDict(arbitrary_types_allowed=True) 

    def to_dict(self):
        return {
            "threshold": self.threshold,
            "user_index": self.user_index,
            "user_id": self.user_id,
            "user_evaluation": self.user_evaluation,
            "group": str(self.group),  # Assuming group has a __str__ method
            "paillier_public_key": {"n": self.paillier_public_key.n},
            "paillier_secret_key": {"p": self.paillier_secret_key.p, "q": self.paillier_secret_key.q},
            "user_modulus": {
                "N": self.user_modulus.N,
                "h1": self.user_modulus.h1,
                "h2": self.user_modulus.h2
            },
            "original_secret_share": self.original_secret_share,
            "num_of_updates": self.num_of_updates,
            "shrinked_secret_share": self.shrinked_secret_share
        }

    @classmethod
    def from_dict(cls, data):
        paillier_pub = paillier.PaillierPublicKey(n=data["paillier_public_key"]["n"])
        paillier_priv = paillier.PaillierPrivateKey(paillier_pub, data["paillier_secret_key"]["p"], data["paillier_secret_key"]["q"])
        user_mod = user_modulus(
            N=data["user_modulus"]["N"],
            h1=data["user_modulus"]["h1"],
            h2=data["user_modulus"]["h2"]
        )
        return cls(
            threshold=data["threshold"],
            user_index=data["user_index"],
            user_id=data["user_id"],
            user_evaluation=data["user_evaluation"],
            group=data["group"],  # Ensure proper deserialization if needed
            paillier_public_key=paillier_pub,
            paillier_secret_key=paillier_priv,
            user_modulus=user_mod,
            original_secret_share=data["original_secret_share"],
            num_of_updates=data["num_of_updates"],
            shrinked_secret_share=data.get("shrinked_secret_share")
        )

class user_index_to_user_id_message(BaseModel):
    index_to_user_id: Dict[int, str]

    def to_dict(self):
        return {
            "index_to_user_id": self.index_to_user_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(index_to_user_id=data["index_to_user_id"])

    def get_type():
        return "user_index_to_user_id"