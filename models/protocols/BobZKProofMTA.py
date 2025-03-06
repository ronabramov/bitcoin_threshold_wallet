from phe import paillier, EncryptedNumber
import random
import gmpy2
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_RegMta_ProverCommitment, Bob_ZKProof_RegMta_Proof_For_Challenge, Bob_ZKProof_RegMta_Settings, Bob_ZKProof_RegMta_Prover_Settings

"""
    Zero Knowledge Proof used by Bob in the case he wants to prove values x,y are small
    Without restriction of x being a discrete log any public value.
    For the latter case, use the BobZKProofMtAwc.
    The prover would convinve the verifier x in [-q^3,q^3] and y in [-q^7,q^7].
    The input for the proof is Paillier Public key (N,Gamma) - Prover, two values c1 and c2 in Z_N^2.
    The prover knows x in Z_q ,y in Z_q^5  and r in Z_N* such that c2 = c1^x * Gamma^y * r^N modN^2.
"""
def pick_element_from_Multiplicative_group(N):
    if N <= 1:
        raise ValueError("N must be greater than 1.")
    
    while True:
        a = random.randint(1, N - 1)
        if gmpy2.gcd(a, N) == 1:
            return a

def prover_generates_commitment(settings : Bob_ZKProof_RegMta_Prover_Settings, enc_a_cipher_valued) -> Bob_ZKProof_RegMta_ProverCommitment:
    """
    :param q: Security parameter or order of the group
    :param paillier_N: Paillier modulus
    :param paillier_Gamma 
    :param Modulus_N: Another modulus used for non-Paillier operations
    :return: Bob ZK Proof Commitment composed of alpha, beta, little_gamma, rho, rho',tau,sigma,z,z',t,v, w
    """
    q = settings.q
    Modulus_N = settings.verifier_modulus.N
    paillier_N = settings.paillier_public_key.n
    h1 = settings.verifier_modulus.h1
    h2 = settings.verifier_modulus.h2
    c1 = enc_a_cipher_valued

    q_third = q ** 3
    q_seventh = q ** 7
    q_third_Modulus_N = q_third * Modulus_N
    paiilier_N_squared = paillier_N ** 2

    alpha = random.randint(0,q_third-1)
    rho = random.randint(0,q * Modulus_N - 1)
    rho_prime = random.randint(0,q_third_Modulus_N-1)
    sigma = random.randint(0,q * Modulus_N - 1)
    beta = pick_element_from_Multiplicative_group(paillier_N)
    little_gamma = random.randint(0,q_seventh - 1)
    tau = random.randint(0,q_third_Modulus_N-1)

    z = (gmpy2.powmod(h1, settings.b, Modulus_N) * gmpy2.powmod(h2, rho, Modulus_N)) % Modulus_N
    z_prime = (gmpy2.powmod(h1, alpha, Modulus_N) * gmpy2.powmod(h2, rho_prime, Modulus_N)) % Modulus_N
    t = (gmpy2.powmod(h1, settings.beta_prime, Modulus_N) * gmpy2.powmod(h2, sigma, Modulus_N)) % Modulus_N
    v = (gmpy2.powmod(c1, alpha, paiilier_N_squared) * gmpy2.powmod(settings.paillier_public_key.g, little_gamma, paiilier_N_squared) 
         * gmpy2.powmod(beta, paillier_N, paiilier_N_squared)) % paiilier_N_squared
    w = (gmpy2.powmod(h1, little_gamma, Modulus_N) * gmpy2.powmod(h2, tau, Modulus_N)) % Modulus_N

    commitment = Bob_ZKProof_RegMta_ProverCommitment(alpha, rho, rho_prime, sigma, beta, little_gamma, tau, z, z_prime, t, v, w)
    return commitment

def verifier_send_challenge(q):
    e = random.randint(1, q - 1)
    return e

def prover_answers_challenge(prover_commitment : Bob_ZKProof_RegMta_ProverCommitment, e, settings : Bob_ZKProof_RegMta_Prover_Settings) -> Bob_ZKProof_RegMta_Proof_For_Challenge:
    
    #Align with ZK proof notation
    x = settings.b
    y= settings.beta_prime
    paillier_N = settings.paillier_public_key.n

    s = (gmpy2.powmod(settings.r, e, paillier_N) * prover_commitment.beta) % paillier_N
    s1 = e * x + prover_commitment.alpha
    s2 = e * prover_commitment.rho + prover_commitment.rho_prime
    t1 = e * y + prover_commitment.gamma
    t2 = e * prover_commitment.sigma + prover_commitment.tau

    proof_for_challenge = Bob_ZKProof_RegMta_Proof_For_Challenge(s=s, s1=s1, s2=s2, t1=t1, t2=t2)
    return proof_for_challenge

def verifier_verify_result(prover_commitment : Bob_ZKProof_RegMta_ProverCommitment, proof_for_challenge : Bob_ZKProof_RegMta_Proof_For_Challenge,
                            e, settings : Bob_ZKProof_RegMta_Settings, enc_a : EncryptedNumber, enc_ab_plus_beta_prime: EncryptedNumber):
    
    enc_a_cipher = enc_a.ciphertext(be_secure=False)
    enc_ab_plus_beta_prime_cipher = enc_ab_plus_beta_prime.ciphertext(be_secure=False)
    q = settings.q
    paillier_N = settings.paillier_public_key.n
    Modulus_N = settings.verifier_modulus.N
    h1 = settings.verifier_modulus.h1
    h2 = settings.verifier_modulus.h2
    paillier_g = settings.paillier_public_key.g

    q_third = q ** 3
    q_seventh = q** 7
    paillier_N_squared = paillier_N ** 2
    valid_s1 = proof_for_challenge.s1 <= q_third
    valid_t1 = proof_for_challenge.t1 <= q_seventh
    
    # Calculation to verify z^e * z_prime 
    calculated_z_power_e_times_z_prime = (gmpy2.powmod(h1, proof_for_challenge.s1, Modulus_N) * gmpy2.powmod(h2, proof_for_challenge.s2, Modulus_N)) % Modulus_N
    value_from_commitment = (gmpy2.powmod(prover_commitment.z, e, Modulus_N) * prover_commitment.z_prime) % Modulus_N
    valid_z_power_e_times_z_prime = calculated_z_power_e_times_z_prime == value_from_commitment

    # Calculation to verify t^e * w 
    calculated_t_power_e_times_w = (gmpy2.powmod(h1, proof_for_challenge.t1, Modulus_N) * gmpy2.powmod(h2, proof_for_challenge.t2, Modulus_N)) % Modulus_N
    value_from_commitment = (gmpy2.powmod(prover_commitment.t, e, Modulus_N) * prover_commitment.w) % Modulus_N
    valid_t_power_e_times_w = calculated_t_power_e_times_w == value_from_commitment

    # Calculation to verify c2^e * v 
    calculated_c2_power_e_times_v = (gmpy2.powmod(enc_a_cipher, proof_for_challenge.s1, paillier_N_squared) 
                                     * gmpy2.powmod(proof_for_challenge.s, paillier_N, paillier_N_squared) 
                                     * gmpy2.powmod(paillier_g, proof_for_challenge.t1, paillier_N_squared)) % paillier_N_squared
    
    value_from_commitment = (gmpy2.powmod(enc_ab_plus_beta_prime_cipher, e, paillier_N_squared) * prover_commitment.v) % paillier_N_squared
    valid_t_power_e_times_v = calculated_c2_power_e_times_v == value_from_commitment

    return valid_s1 and valid_t1 and valid_z_power_e_times_z_prime and valid_t_power_e_times_w and valid_t_power_e_times_v

def pick_r(paillier_N):
    return pick_element_from_Multiplicative_group(paillier_N)

def caculate_c2(r, x, y, public_key : paillier.PaillierPublicKey, enc_a):
    c2 = ( gmpy2.powmod(enc_a, x, public_key.nsquare) * gmpy2.powmod(public_key.g, y, public_key.nsquare) * 
          gmpy2.powmod(r, public_key.n, public_key.nsquare)) % public_key.nsquare    
    
    return enc_a,c2




# RON TODO : We should move the selection of h1,h2, public keys etc to the appropriate places
#            They should be passed as arguments.
# x = 11
# y = 13
# public_key, secret_key = paillier.generate_paillier_keypair()
# r = pick_r(public_key.n)
# c1 = random.randint(0 , public_key.nsquare)
# c2 = (gmpy2.powmod(c1, x, public_key.nsquare) * gmpy2.powmod(public_key.g, y, public_key.nsquare) * gmpy2.powmod(r, public_key.n, public_key.nsquare)) % public_key.nsquare
# verifier_settings_for_proof = Bob_ZKProof_RegMta_Settings(q = 13, public_key=public_key, Modulus_N=99, h1 = 13, h2=23, c1=c1, c2=c2 )
# prover_settings_for_proof = Bob_ZKProof_RegMta_Prover_Settings(q =13, public_key=public_key, Modulus_N=99, h1 = 13, h2 = 23, r=r, c1=c1, c2=c2, b=x, beta_prime=y)
# #Test 1 : Should pass - valid arguments#
# prover_commitment = prover_generates_commitment(prover_settings_for_proof)
# challenge = verifier_send_challenge(verifier_settings_for_proof.Modulus_N)
# proof_for_challenge = prover_answers_challenge(prover_commitment, challenge, prover_settings_for_proof)
# result = verifier_verify_result(prover_commitment, proof_for_challenge, challenge, verifier_settings_for_proof)
