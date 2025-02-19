from pydantic import BaseModel
from models.DTOs.message_dto import MessageType
"""
DTO object for Schnorr ZK proof of value x
"""

class value_knowledge_zk_proof(BaseModel):
    R_x : int
    s : int
    
    @property
    def type(self):
        return MessageType.ValueKnowledgeZkProof
