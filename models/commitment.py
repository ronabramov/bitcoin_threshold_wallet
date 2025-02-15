from models.algorithm_step import Algorithm_Step
from phe import paillier
from pydantic import BaseModel, ConfigDict


class Commitment(BaseModel):
    algorithm_step: Algorithm_Step
    committing_user_index: int
    committed_values: list[int]
    paillier_public_key: paillier.PaillierPublicKey
    model_config = ConfigDict(arbitrary_types_allowed=True) 

    def to_dict(self):
        """Serialize to a dictionary that can be converted to JSON."""
        return {
            "algorithm_step": self.algorithm_step.to_dict() if hasattr(self.algorithm_step, "to_dict") else str(self.algorithm_step),
            "committing_user_index": self.committing_user_index,
            "committed_values": self.committed_values,
            "paillier_public_key": {
                "n": self.paillier_public_key.n  # Store only `n`, enough to reconstruct the key
            }
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dictionary and reconstruct PaillierPublicKey."""
        paillier_pub = paillier.PaillierPublicKey(n=data["paillier_public_key"]["n"])
        algorithm_step = Algorithm_Step.from_dict(data["algorithm_step"]) if hasattr(Algorithm_Step, "from_dict") else data["algorithm_step"]
        
        return cls(
            algorithm_step=algorithm_step,
            committing_user_index=data["committing_user_index"],
            committed_values=data["committed_values"],
            paillier_public_key=paillier_pub  # Fully functional Paillier key
        )
