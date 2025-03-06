import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../bitcoin_threshold_wallet')))

import random
import gmpy2
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from models.models import user_modulus
from phe import paillier, PaillierPrivateKey, PaillierPublicKey, EncodedNumber, EncryptedNumber

"""
Arguments : 
user_modulus : N,h1,h2 are of the Verifier
paillier public key - Prover
"""
def pick_element_from_Multiplicative_group(N):
    if N <= 1:
        raise ValueError("N must be greater than 1.")
    
    while True:
        a = random.randint(1, N - 1)
        if gmpy2.gcd(a, N) == 1:
            return a

def enc_x(x, r, paillier_pub_key : PaillierPublicKey):
    """
    return Enc_A(x)
    """
    return paillier_pub_key.encrypt(value=x, r_value=r)

def dec_value(encrypted_value : EncryptedNumber, paillier_secret_key : PaillierPrivateKey):
    return paillier_secret_key.decrypt(encrypted_number=encrypted_value)

def pick_r(paillier_N):
    return pick_element_from_Multiplicative_group(paillier_N)

def prover_generates_commitment(q, paillier_N, paillier_Gamma, verifier_modulus : user_modulus, a) -> AliceZKProof_Commitment:
    """
    Generate and return commitments and related values as a dictionary.
    
    :param q: Security parameter or order of the group
    :param paillier_N: Prover's Paillier N
    :param paillier_Gamma: Prover's Paillier G
    :param Modulus_N: Verifier Modulus_N
    :return: Alice ZK Proof Commitment composed of alpha, beta, little_gamma, rho, z, u, w
    """
    
    q_third = q ** 3
    Modulus_N = verifier_modulus.N
    h1 = verifier_modulus.h1
    h2 = verifier_modulus.h2
    q_third_Modulus_N = q_third * Modulus_N
    alpha = random.randint(1,q_third-1)
    beta = pick_element_from_Multiplicative_group(paillier_N)
    little_gamma = random.randint(0,q_third_Modulus_N-1)
    rho = random.randint(1,q * Modulus_N - 1)
    z = (gmpy2.powmod(h1, a, Modulus_N) * gmpy2.powmod(h2, rho, Modulus_N)) % Modulus_N
    u = (gmpy2.powmod(paillier_Gamma, alpha, paillier_N**2) * gmpy2.powmod(beta, paillier_N, paillier_N**2)) % (paillier_N**2)
    w = (gmpy2.powmod(h1, alpha, Modulus_N) * gmpy2.powmod(h2, little_gamma, Modulus_N)) % Modulus_N

    commitment = AliceZKProof_Commitment(alpha, beta, little_gamma, rho, z, u, w)
    return commitment

def verifier_send_challenge(q):
    e = random.randint(1, q - 1)
    return e

def prover_answers_challenge(alpha, beta, little_gamma, rho, r, e, a, paillier_N) -> AliceZKProof_Proof_For_Challenge:
    s = (gmpy2.powmod(r, e, paillier_N) * beta) % paillier_N
    s1 = e * a + alpha
    s2 = e * rho + little_gamma

    proof_for_challenge = AliceZKProof_Proof_For_Challenge(s=s, s1=s1, s2=s2)
    return proof_for_challenge

def verifier_verify_result(z, u, w, s, s1, s2, e, enc_a: EncryptedNumber, q, user_modulus, paillier_N, paillier_g):
    q_third = q ** 3
    valid_s1 = s1 <= q_third
    Modulus_N = user_modulus.N
    h1 = user_modulus.h1
    h2 = user_modulus.h2
    # Use the raw (non-obfuscated) ciphertext
    enc_a_ciphertext = enc_a.ciphertext(be_secure=False)
    paillier_g_s1 = gmpy2.powmod(paillier_g, s1, paillier_N**2)
    s_paillier_N = gmpy2.powmod(s, paillier_N, paillier_N**2)
    enc_a_inv_e = gmpy2.invert(gmpy2.powmod(enc_a_ciphertext, e, paillier_N**2), paillier_N**2)
    calculated_u = (paillier_g_s1 * s_paillier_N * enc_a_inv_e) % (paillier_N**2)
    
    valid_u = calculated_u == u

    # Calculate w to verify
    h1_s1 = gmpy2.powmod(h1, s1, Modulus_N)
    h2_s2 = gmpy2.powmod(h2, s2, Modulus_N)
    z_inv_e = gmpy2.powmod(gmpy2.invert(z, Modulus_N), e, Modulus_N)
    calculated_w = (h1_s1 * h2_s2 * z_inv_e) % Modulus_N
    valid_w = calculated_w == w

    return valid_s1 and valid_u and valid_w



######
#Tests
######
# q = 13
# N = 99
# h1 = 13
# h2 = 23
# #Test 1 : Should pass - valid arguments#
# a = 11
# public_key, secret_key = paillier.generate_paillier_keypair()
# r = pick_r(public_key.n)
# c = calculate_c(public_key.g, a, public_key.n, r)
# commitment = prover_generates_commitment(q=q, paillier_N=public_key.n, Modulus_N=N, paillier_Gamma=public_key.g, a=a)
# e = verifier_send_challenge(Modulus_N=N)
# proof_for_challenge = prover_answers_challenge(commitment.alpha, commitment.beta, commitment.gamma, commitment.rho, r, e, a, public_key.n)
# result = verifier_verify_result(commitment.z,commitment.u,commitment.w,proof_for_challenge.s,proof_for_challenge.s1,proof_for_challenge.s2,e,c,q,h1,h2,N,public_key.n,public_key.g)
# #####
# #Test 2 : Should fail - non valid a#
# a = 20000
# public_key, secret_key = paillier.generate_paillier_keypair()
# r = pick_r(public_key.n)
# c = calculate_c(public_key.g, a, public_key.n, r)
# commitment = prover_generates_commitment(q=q, paillier_N=public_key.n, Modulus_N=N, paillier_Gamma=public_key.g, a=a)
# e = verifier_send_challenge(Modulus_N=N)
# proof_for_challenge = prover_answers_challenge(commitment.alpha, commitment.beta, commitment.gamma, commitment.rho, r, e, a, public_key.n)
# result = verifier_verify_result(commitment.z,commitment.u,commitment.w,proof_for_challenge.s,proof_for_challenge.s1,proof_for_challenge.s2,e,c,q,h1,h2,N,public_key.n,public_key.g)
# #######
value_to_encrypt = 5
public_key, secret_key = paillier.generate_paillier_keypair() 
r = pick_r(public_key.n)
x = enc_x(x=value_to_encrypt, r=r, paillier_pub_key=public_key)
y = dec_value(encrypted_value=x, paillier_secret_key=secret_key)
print(f'encrypted value : {x} , DecryptedValue = {y} of original value {value_to_encrypt}')
