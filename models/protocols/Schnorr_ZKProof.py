import os
import hashlib
from ecdsa import SECP256k1,curves

class Schnorr_ZK_Proof:
    """
    Using input Eliptic Curve from ECDSA 
    Hashing via sha256
    Implementing two phase - version of Schnorr ZK proof for knowing a value.
    Will be Used in the Last steps of Signature Generation alg.
    """
    def __init__(self, curve: curves.Curve):
        self.curve = curve
        self.G = curve.generator
        self.q = curve.order

    def provide_zk_proof_for_input(self, x):
        """ Generate a zero-knowledge proof using a numeric private key """
        # Generate a random nonce k, Calculate the nonce point R = k*G
        k = int.from_bytes(os.urandom(32), byteorder="big") % self.q
        R = k * self.G
        R_x = R.x()

        # Hash the concatenation of R_x and the public key
        public_key = x * self.G
        e = hashlib.sha256(R_x.to_bytes(32, byteorder="big") + public_key.to_bytes()).digest()
        e = int.from_bytes(e, byteorder="big") % self.q

        # Calculate the challenge response s = k - e*private_key
        s = (k - e * x) % self.q

        return (R_x, s)

    def verify_knowledge(self, public_point, proof):
        """ Verify a Schnorr ZKP with a numeric public key """
        R_x, s = proof

        # Calculate e from the hash of R_x and public key
        e = hashlib.sha256(R_x.to_bytes(32, byteorder="big") + public_point.to_bytes()).digest()
        e = int.from_bytes(e, byteorder="big") % self.q

        # Calculate R' = s*G + e*public_key
        R_prime = s * self.G + e * public_point

        # Verify the x-coordinate matches the provided R_x
        return R_prime.x() == R_x

# Example usage
# schnor_zk_protocol = Schnorr_ZK_Proof(SECP256k1) # example group from ECDSA
# private_key = 123456789  # Some private key as an integer
# public_key = private_key * schnor_zk_protocol.G

# proof = schnor_zk_protocol.provide_zk_proof_for_input(private_key)
# print("Proof:", proof)
# assert schnor_zk_protocol.verify_knowledge(public_key, proof)
# print("Verification: Successful")
