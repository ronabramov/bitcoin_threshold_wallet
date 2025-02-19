from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
from typing import List, Optional, Dict
from ecdsa.ellipticcurve import PointJacobi, CurveFp
from ecdsa.curves import Curve, SECP256k1
from ecdsa import curves
from phe import paillier
from models.DTOs.message_dto import MessageType

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


class user_modulus(BaseModel):
    N : int
    h1 : int
    h2: int 

class key_generation_share(BaseModel):
    """
    Consider p as the polynomial generated by the user produced this share.
    target_user_evaluation : evaulated polynomial at target user index
    v_i = g^ai - where ai is the coefficient of the shamir polynomial generated by generating user
    v_0 - g^secret
    This share can be tested for validness through Feldaman_VSS_Protocl.Verify_Share method.
    curve : The curved used for the generation.
    """
    generating_user_index : int
    target_user_matrix_id : Optional[str] = None # Will be filled right before sending message. 
    target_user_index : int
    target_user_evaluation : int
    v_i: Optional[List[PointJacobi]] = None
    v_0 : Optional[PointJacobi]
    curve : str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self):

        def serialize_point(p):
            if isinstance(p, PointJacobi):
                affine_p = p.to_affine()  
                return {"x": int(affine_p.x()), "y": int(affine_p.y())}  #  Convert mpz to int
            return None  
        
        curve_instance = curves.curve_by_name(self.curve)

        if hasattr(curve_instance, "curve"): 
            curve_fp = curve_instance.curve  
            curve_data = {
                "p": int(curve_fp.p()), 
                "a": int(curve_fp.a()),
                "b": int(curve_fp.b()),
                "order": int(curve_instance.order),
                "name": self.curve
            }
        else:
            raise AttributeError(f"Curve {self.curve} does not have a valid curve definition.")


        return {
            "generating_user_index": self.generating_user_index,
            "target_user_matrix_id": self.target_user_matrix_id,
            "target_user_index": self.target_user_index,
            "target_user_evaluation": self.target_user_evaluation,
            "v_i": [serialize_point(p) for p in self.v_i if p is not None],  
            "v_0": serialize_point(self.v_0),  
            "curve": curve_data
        }


    @classmethod
    def from_dict(cls, data):
        """Deserialize and reconstruct elliptic curve points inside the object."""
        def deserialize_point(p):
            """ Convert dictionary back to PointJacobi using public methods. """
            if p is not None:
                return PointJacobi(curve_instance, int(p["x"]), int(p["y"]), 1) # 1 as default of affine coordinates
            return None
        
        curve_data = data["curve"]
        curve_instance = CurveFp(
            int(curve_data["p"]),
            int(curve_data["a"]),
            int(curve_data["b"]),
            int(curve_data["order"]),
            name=curve_data["name"]
        )
        v_0 = deserialize_point(data["v_0"])
        v_i = [deserialize_point(p) for p in data["v_i"] if p is not None]

        return cls(
            generating_user_index=data["generating_user_index"],
            target_user_matrix_id=data["target_user_matrix_id"],
            target_user_index=data["target_user_index"],
            target_user_evaluation=data["target_user_evaluation"],
            v_i=v_i,
            v_0=v_0,
            curve=curve_data["name"]
        )




class user_public_share(BaseModel):
    user_index: int
    user_id: str
    paillier_public_key: paillier.PaillierPublicKey
    user_modulus: user_modulus

    model_config = ConfigDict(arbitrary_types_allowed=True) 

    @field_serializer("paillier_public_key")
    def serialize_public_key(self, pub_key):
        return {"n": str(pub_key.n)}

    @field_serializer("paillier_secret_key")
    def serialize_private_key(self, priv_key):
        return {
            "p": str(priv_key.p),
            "q": str(priv_key.q)
        }

    @field_validator("paillier_public_key", mode="before")
    def deserialize_public_key(cls, value):
        if isinstance(value, dict):  # If already deserialized
            return paillier.PaillierPublicKey(n=int(value["n"]))
        return value  # Already an object

    @field_validator("paillier_secret_key", mode="before")
    def deserialize_private_key(cls, value):
        if isinstance(value, dict):  # If already deserialized
            pub_key = paillier.PaillierPublicKey(n=int(value["p"]) * int(value["q"]))  # Reconstruct public key
            return paillier.PaillierPrivateKey(pub_key, int(value["p"]), int(value["q"]))
        return value  # Already an object


    # def to_dict(self):
    #     return {
    #         "user_index": self.user_index,
    #         "user_id": self.user_id,
    #         "paillier_public_key": {"n": self.paillier_public_key.n},  # Store only `n`
    #         "user_modulus": {
    #             "N": self.user_modulus.N,
    #             "h1": self.user_modulus.h1,
    #             "h2": self.user_modulus.h2
    #         }
    #     }

    # @classmethod
    # def from_dict(cls, data):
    #     paillier_pub = paillier.PaillierPublicKey(n=data["paillier_public_key"]["n"])
    #     user_mod = user_modulus(
    #         N=data["user_modulus"]["N"],
    #         h1=data["user_modulus"]["h1"],
    #         h2=data["user_modulus"]["h2"]
    #     )
    #     return cls(
    #         user_index=data["user_index"],
    #         user_id=data["user_id"],
    #         paillier_public_key=paillier_pub,
    #         user_modulus=user_mod,
    #     )

    def get_type():
        return "user_public_share"   

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
    user_evaluation: Optional[int] = None
    group: str
    paillier_public_key: paillier.PaillierPublicKey
    paillier_secret_key: paillier.PaillierPrivateKey
    user_modulus: user_modulus
    num_of_updates: int = 0
    original_secret_share: Optional[int] = None
    shrinked_secret_share: Optional[int] = None
    model_config = ConfigDict(arbitrary_types_allowed=True) 
    
    @field_serializer("paillier_public_key")
    def serialize_public_key(self, pub_key):
        return {"n": str(pub_key.n)}

    @field_serializer("paillier_secret_key")
    def serialize_private_key(self, priv_key):
        return {
            "p": str(priv_key.p),
            "q": str(priv_key.q)
        }

    @field_validator("paillier_public_key", mode="before")
    def deserialize_public_key(cls, value):
        if isinstance(value, dict):  # If already deserialized
            return paillier.PaillierPublicKey(n=int(value["n"]))
        return value  # Already an object

    @field_validator("paillier_secret_key", mode="before")
    def deserialize_private_key(cls, value):
        if isinstance(value, dict):  # If already deserialized
            pub_key = paillier.PaillierPublicKey(n=int(value["p"]) * int(value["q"]))  # Reconstruct public key
            return paillier.PaillierPrivateKey(pub_key, int(value["p"]), int(value["q"]))
        return value  # Already an object

    # def to_dict(self):
    #     return {
    #         "threshold": self.threshold,
    #         "user_index": self.user_index,
    #         "user_id": self.user_id,
    #         "user_evaluation": self.user_evaluation,
    #         "group": self.group,
    #         "paillier_public_key": {"n": str(self.paillier_public_key.n)},
    #         "paillier_secret_key": {"p": str(self.paillier_secret_key.p), "q": str(self.paillier_secret_key.q)},
    #         "user_modulus": {
    #             "N": self.user_modulus.N,
    #             "h1": self.user_modulus.h1,
    #             "h2": self.user_modulus.h2
    #         },
    #         "original_secret_share": self.original_secret_share,
    #         "num_of_updates": self.num_of_updates,
    #         "shrinked_secret_share": self.shrinked_secret_share
    #     }

    # @classmethod
    # def from_dict(cls, data):
    #     paillier_pub = paillier.PaillierPublicKey(n=int(data["paillier_public_key"]["n"]))
    #     paillier_priv = paillier.PaillierPrivateKey(paillier_pub, int(data["paillier_secret_key"]["p"]), int(data["paillier_secret_key"]["q"]))
    #     user_mod = user_modulus(
    #         N=data["user_modulus"]["N"],
    #         h1=data["user_modulus"]["h1"],
    #         h2=data["user_modulus"]["h2"]
    #     )
    #     return cls(
    #         threshold=data["threshold"],
    #         user_index=data["user_index"],
    #         user_id=data["user_id"],
    #         user_evaluation=data["user_evaluation"],
    #         group=data["group"],
    #         paillier_public_key=paillier_pub,
    #         paillier_secret_key=paillier_priv,
    #         user_modulus=user_mod,
    #         original_secret_share=data["original_secret_share"],
    #         num_of_updates=data["num_of_updates"],
    #         shrinked_secret_share=data.get("shrinked_secret_share")
    #     )

class user_index_to_user_id_message(BaseModel):
    index_to_user_id: Dict[int, str]

    def to_dict(self):
        return {
            "index_to_user_id": self.index_to_user_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(index_to_user_id=data["index_to_user_id"])
