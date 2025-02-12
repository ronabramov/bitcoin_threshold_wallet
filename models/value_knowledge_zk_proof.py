from pydantic import BaseModel

"""
DTO object for Schnorr ZK proof of value x
"""

class value_knowledge_zk_proof(BaseModel):
    R_x : int
    s : int