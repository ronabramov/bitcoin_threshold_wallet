from ecdsa import SigningKey, SECP256k1
import os
import hashlib

"""
Schnorr ZK Proof.
At the moment usage hardcoded the SECPk1 curve.
Not a must - use the same curve from other protocols.
"""

def schnorr_zkp_prove(private_key):
    """ Generate a zero-knowledge proof of possession of a private key """
    # Generate a random nonce
    k = os.urandom(SECP256k1.baselen)
    k = int.from_bytes(k, byteorder="big") % SECP256k1.order

    # Calculate the nonce point R
    R = k * SECP256k1.generator
    R_x = R.x()

    # Hash the concatenation of R_x and the public key
    e = hashlib.sha256(R_x.to_bytes(32, byteorder="big") + private_key.get_verifying_key().to_string()).digest()
    e = int.from_bytes(e, byteorder="big") % SECP256k1.order

    # Calculate the challenge response s
    s = (k - e * int.from_bytes(private_key.to_string(), "big")) % SECP256k1.order

    return (R_x, s)

def schnorr_zkp_verify(public_key, proof):
    """ Verify a Schnorr zero-knowledge proof """
    R_x, s = proof
    e = hashlib.sha256(R_x.to_bytes(32, byteorder="big") + public_key.to_string()).digest()
    e = int.from_bytes(e, byteorder="big") % SECP256k1.order

    # Calculate the point R using s and e
    R = s * SECP256k1.generator + e * public_key.pubkey.point

    # Verify the x-coordinate matches the provided R_x
    return R.x() == R_x

# Usage
private_key = SigningKey.generate(curve=SECP256k1)
public_key = private_key.get_verifying_key()

proof = schnorr_zkp_prove(private_key)
print("Proof:", proof)
assert schnorr_zkp_verify(public_key, proof)
print("Verification: Successful")

#Failing test:
new_x = proof[0]
new_x +=1
new_proof = new_x, proof[1]
assert not schnorr_zkp_verify(public_key, new_proof)
print("Verification Failed")

