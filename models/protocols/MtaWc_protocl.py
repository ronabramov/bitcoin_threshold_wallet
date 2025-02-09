from phe import paillier, EncryptedNumber
import random
import AliceZKProof
from AliceZKProofModules import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from BobZKProofMtAModules import Bob_ZKProof_RegMta_Proof_For_Challenge, Bob_ZKProof_RegMta_ProverCommitment, Bob_ZKProof_RegMta_Settings, Bob_ZKProof_RegMta_Prover_Settings
import BobZKProofMtaWc 
from ecdsa import NIST256p, curves


"""
    Mta Protocol : Alice holds value a, Bob holds value b.
    At the end of the protocol Alice will hold alpha and Bob will hold beta
    s.t a * b = alpha + beta.
    Neither one of the participants will learn anything about the other's data.
    Using ZK proofs both Alice and Bob proving their values are in the valid ranges. 
"""


class MtaWcProtocolWithZKP:
    # TODO: 
    # Instead of having the values as properties and use them along the class 
    # We should activate the methods and send the corresponding arguments in the relevnat places. 

    def __init__(self, Alice_verifier_modulus_N, Alice_h1, Alice_h2, Bob_verifier_Modulus_N, Bob_h1, Bob_h2, a_value = None, b_value = None, curve : curves.Curve = NIST256p ):
        self.q = curve.order
        self.Alice_Alg_verifier_modulus_N = Alice_verifier_modulus_N 
        self.Alice_Alg_h1 = Alice_h1
        self.Alice_Alg_h2 = Alice_h2
        self.Alice_Alg_public_key, self.Alice_Alg_private_key = paillier.generate_paillier_keypair()
        self.Alice_Alg_prover_paillier_N = self.Alice_Alg_public_key.n
        self.Alice_Alg_prover_paillier_Gamma = self.Alice_Alg_public_key.g
        self.Alice_Alg_r = AliceZKProof.pick_r(self.Alice_Alg_prover_paillier_N)
        self.Alice_Alg_c = AliceZKProof.calculate_c(self.Alice_Alg_prover_paillier_Gamma, a_value, self.Alice_Alg_prover_paillier_N, self.Alice_Alg_r)
        Bob_Alg_verifier_Modulus_N = Bob_verifier_Modulus_N
        Bob_Alg_h1 = Bob_h1
        Bob_Alg_h2 = Bob_h2
        Bob_Alg_Beta_Prime = random.randint(1, self.q ** 5) # veta_prime in Z_q^5
        Bob_Alg_Public_key = paillier.generate_paillier_keypair()[0] # Should be passed as argument
        Bob_Alg_r = BobZKProofMtaWc.pick_r(Bob_Alg_Public_key.n)
        Bob_Alg_c1, Bob_Alg_c2 = BobZKProofMtaWc.pick_c1_and_c2(r=Bob_Alg_r, x = b_value,y=Bob_Alg_Beta_Prime,public_key= Bob_Alg_Public_key)
        self.Bob_Alg_verifier_Settings = Bob_ZKProof_RegMta_Settings(public_key=Bob_Alg_Public_key, Modulus_N=Bob_Alg_verifier_Modulus_N,
                                                             h1 = Bob_Alg_h1, h2=Bob_Alg_h2, c1=Bob_Alg_c1, c2=Bob_Alg_c2, curve=curve)
        self.bob_alg_prover_settings = Bob_ZKProof_RegMta_Prover_Settings(Bob_Alg_Public_key, Modulus_N=Bob_Alg_verifier_Modulus_N, h1=Bob_Alg_h1,
                                                    h2 = Bob_Alg_h2, r= Bob_Alg_r, c1= Bob_Alg_c1, c2= Bob_Alg_c2, b=b_value,
                                                     curve=curve, beta_prime=Bob_Alg_Beta_Prime)


    def encrypt_value(self, value) -> EncryptedNumber:
        return self.Alice_Alg_public_key.encrypt(value)


    def decrypt_value(self, encrypted_value):
        return self.Alice_Alg_private_key.decrypt(encrypted_value)


    def alice_encrypting_a_and_sending_commitment(self, a):
        """Alice encrypts a, generates corresponding commitment , and sends both"""
        enc_a = self.encrypt_value(a)
        commitment_of_a : AliceZKProof_Commitment = AliceZKProof.prover_generates_commitment(self.q, self.Alice_Alg_prover_paillier_N, 
                                                                                             self.Alice_Alg_prover_paillier_Gamma, self.Alice_Alg_verifier_modulus_N,
                                                                                               a, self.Alice_Alg_h1, self.Alice_Alg_h2)
        return enc_a, self.Alice_Alg_public_key, commitment_of_a
    

    def bob_challenging_a_commitment(self):
        return AliceZKProof.verifier_send_challenge(self.q)
    

    def alice_sends_proof_answering_challenge(self, commitment_of_a : AliceZKProof_Commitment, a, verifier_challenge) -> AliceZKProof_Proof_For_Challenge:
        return AliceZKProof.prover_answers_challenge(commitment_of_a.alpha, commitment_of_a.beta, commitment_of_a.gamma, commitment_of_a.rho, self.Alice_Alg_r,
                                                      verifier_challenge, a, self.Alice_Alg_prover_paillier_N)


    def bob_verify_a_commiting_encrypting_b(self, enc_a : EncryptedNumber, public_key, challenge, proof_of_a : AliceZKProof_Proof_For_Challenge,
                                               commitment_of_a : AliceZKProof_Commitment, prover_settings : Bob_ZKProof_RegMta_Prover_Settings):
        
        """Bob verifies Alice's proof, then computes E(ab + beta') and proves correctness"""
        verified_a_value = AliceZKProof.verifier_verify_result(commitment_of_a.z, commitment_of_a.u, commitment_of_a.w, proof_of_a.s, proof_of_a.s1, 
                                                               proof_of_a.s2, challenge, self.Alice_Alg_c, self.q, self.Alice_Alg_h1, self.Alice_Alg_h2, 
                                                               self.Alice_Alg_verifier_modulus_N, self.Alice_Alg_prover_paillier_N, self.Alice_Alg_prover_paillier_Gamma)
        
        if not verified_a_value:
            raise ValueError("Alice failed ZK proof!")

        b = prover_settings.b
        beta_prime = prover_settings.beta_prime
        enc_beta_prime = public_key.encrypt(beta_prime)

        # Homomorphic computation
        enc_result = enc_a * b + enc_beta_prime  # E(ab + β')
        b_and_beta_prime_commitment = BobZKProofMtaWc.prover_generates_commitment(settings=prover_settings)
        return enc_result, beta_prime, b_and_beta_prime_commitment  # Send commitment to Alice
    

    def alice_challenging_bob_commitment(self):
        return BobZKProofMtaWc.verifier_send_challenge(self.q)
    
    def bob_provide_proof_for_alice_challenge(self, commitment_of_b_and_beta_prime : Bob_ZKProof_RegMta_ProverCommitment,
                                                settings : Bob_ZKProof_RegMta_Prover_Settings, challenge):
        """Given Alice's challenge, Bob provides a proof"""
        return BobZKProofMtaWc.prover_answers_challenge(commitment_of_b_and_beta_prime, challenge, settings)

    def alice_finalize(self, proof_for_challenge : Bob_ZKProof_RegMta_Proof_For_Challenge, commitment : Bob_ZKProof_RegMta_ProverCommitment,
                        enc_result, settings : Bob_ZKProof_RegMta_Settings, challenge):
        """Alice verifies Bob's proof, decrypts and computes her additive share of ab"""
        alice_approves_bob_proof_result = BobZKProofMtaWc.verifier_verify_result(commitment, proof_for_challenge, challenge, settings)
        
        if not alice_approves_bob_proof_result:
            raise ValueError("Bob failed ZK proof!")

        decrypted_value = self.decrypt_value(enc_result)
        alpha = decrypted_value % self.Bob_Alg_verifier_Settings.Modulus_N
        return alpha  # Alice holds α only

    def bob_finalize(self, beta_prime):
        """Bob computes β = his additive share of ab """
        beta = (-beta_prime) % self.Bob_Alg_verifier_Settings.Modulus_N  # Mod q assumption
        return beta  # Bob holds β only


curve = NIST256p
N = 99  #Modulus

h1 = 13
h2 = 23
# Alice's secret
a = 11

# Bob's secret
b = 5

# Example run
mta = MtaWcProtocolWithZKP(N, h1, h2, N, h1, h2, a, b, curve)  #For example both Alice and Bob having the same Paillier Keys and


# Protocol execution
enc_a, pub_key, commitment_of_a = mta.alice_encrypting_a_and_sending_commitment(a)
bob_challenges_alice = mta.bob_challenging_a_commitment()
proof_for_challenge = mta.alice_sends_proof_answering_challenge(commitment_of_a, a, bob_challenges_alice)
enc_result, beta_prime, bob_commitment = mta.bob_verify_a_commiting_encrypting_b(enc_a, pub_key, bob_challenges_alice,proof_for_challenge,
                                                                                 commitment_of_a, mta.bob_alg_prover_settings)
alice_challenges_bob = mta.alice_challenging_bob_commitment()
bob_proof_for_alice_challenge = mta.bob_provide_proof_for_alice_challenge(bob_commitment,mta.bob_alg_prover_settings,alice_challenges_bob)
alpha = mta.alice_finalize(bob_proof_for_alice_challenge, bob_commitment, enc_result, mta.Bob_Alg_verifier_Settings, alice_challenges_bob)
beta = mta.bob_finalize(beta_prime)

# Verify correctness
assert (alpha + beta) % N == (a * b) % N
print(f"Alice's share: {alpha}, Bob's share: {beta}")
