from phe import paillier, EncryptedNumber
import random
import AliceZKProof
from AliceZKProofModules import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from BobZKProofMtAModules import Bob_ZKProof_RegMta_Proof_For_Challenge, Bob_ZKProof_RegMta_ProverCommitment, Bob_ZKProof_RegMta_Settings
import BobZKProofMTA 



class MTAProtocolWithZKP:
    # TODO: 
    # Instead of having the values as properties and use them along the class 
    # We should activate the methods and send the corresponding arguments in the relevnat places. 

    def __init__(self, q, Alice_verifier_modulus_N, Alice_h1, Alice_h2, Bob_verifier_Modulus_N, Bob_h1, Bob_h2, a_value = None, b_value = None ):
        self.q = q
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
        Bob_Alg_Public_key = paillier.generate_paillier_keypair()[0] # Should be passed as argument
        Bob_Alg_r = BobZKProofMTA.pick_r(Bob_Alg_Public_key.n)
        Bob_Alg_c1, Bob_Alg_c2 = BobZKProofMTA.pick_c1_and_c2(Bob_Alg_r, b_value, Bob_Alg_Public_key) # beta prime is needed here. 
        self.Bob_Alg_Settings = Bob_ZKProof_RegMta_Settings(self.q, public_key=Bob_Alg_Public_key, Modulus_N=Bob_Alg_verifier_Modulus_N,
                                                             h1 = Bob_Alg_h1, h2=Bob_Alg_h2, r=Bob_Alg_r, c1=Bob_Alg_c1, c2=Bob_Alg_c2)


    def encrypt_value(self, value) -> EncryptedNumber:
        return self.Alice_Alg_public_key.encrypt(value)


    def decrypt_value(self, encrypted_value):
        return self.Alice_Alg_private_key.decrypt(encrypted_value)


    def alice_encrypting_a_and_sending_commitment(self, a):
        """Alice encrypts a, generates corresponding commitment , and sends both"""
        enc_a = self.encrypt_value(a)
        commitment_of_a : AliceZKProof_Commitment = AliceZKProof.prover_generates_commitment(self.q, self.Alice_Alg_prover_paillier_N, 
                                                                                             self.Alice_Alg_prover_paillier_Gamma, self.Alice_Alg_verifier_modulus_N, a)
        return enc_a, self.Alice_Alg_public_key, commitment_of_a
    

    def bob_challenging_a_commitment(self, public_key, commitment_of_a):
        return AliceZKProof.verifier_send_challenge(self.Alice_Alg_verifier_modulus_N)
    

    def alice_sends_proof_answering_challenge(self, commitment_of_a : AliceZKProof_Commitment, a, verifier_challenge) -> AliceZKProof_Proof_For_Challenge:
        return AliceZKProof.prover_answers_challenge(commitment_of_a.alpha, commitment_of_a.beta, commitment_of_a.gamma, commitment_of_a.rho, self.Alice_Alg_r,
                                                      verifier_challenge, a, self.Alice_Alg_prover_paillier_N)


    def bob_verify_a_commiting_encrypting_b(self, enc_a : EncryptedNumber, public_key, challenge, proof_of_a : AliceZKProof_Proof_For_Challenge,
                                               commitment_of_a : AliceZKProof_Commitment, b):
        
        """Bob verifies Alice's proof, then computes E(ab + beta') and proves correctness"""
        verified_a_value = AliceZKProof.verifier_verify_result(commitment_of_a.z, commitment_of_a.u, commitment_of_a.w, proof_of_a.s, proof_of_a.s1, 
                                                               proof_of_a.s2, challenge, self.Alice_Alg_c, self.q, self.Alice_Alg_h1, self.Alice_Alg_h2, 
                                                               self.Alice_Alg_verifier_modulus_N, self.Alice_Alg_prover_paillier_N, self.Alice_Alg_prover_paillier_Gamma)
        
        if not verified_a_value:
            raise ValueError("Alice failed ZK proof!")

        beta_prime = random.randint(1, self.q ** 5)  # β' chosen u.a.r from Z_q^5 
        enc_beta_prime = public_key.encrypt(beta_prime)

        # Homomorphic computation
        enc_result = enc_a * b + enc_beta_prime  # E(ab + β')
        b_and_beta_prime_commitment = BobZKProofMTA.prover_generates_commitment(settings=self.Bob_Alg_Settings, x=b, y=beta_prime)
        return enc_result, beta_prime, b_and_beta_prime_commitment  # Send commitment to Alice
    

    def alice_challenging_a_commitment(self, public_key, commitment_of_b_and_beta_prime):
        return BobZKProofMTA.verifier_send_challenge(self.Bob_Alg_Settings.Modulus_N)
    
    def bob_provide_proof_for_alice_challenge(self, commitment_of_b_and_beta_prime : Bob_ZKProof_RegMta_ProverCommitment,
                                                settings : Bob_ZKProof_RegMta_Settings, b , beta_prime, challenge):
        """Given Alice's challenge, Bob provides a proof"""
        return BobZKProofMTA.prover_answers_challenge(commitment_of_b_and_beta_prime, b, beta_prime, settings.r, challenge, settings.paillier_public_key.n)

    def alice_finalize(self, proof_for_challenge : Bob_ZKProof_RegMta_Proof_For_Challenge, commitment : Bob_ZKProof_RegMta_ProverCommitment,
                        enc_result, settings : Bob_ZKProof_RegMta_Settings, challenge):
        """Alice verifies Bob's proof, decrypts and computes her additive share of ab"""
        alice_approves_bob_proof_result = BobZKProofMTA.verifier_verify_result(commitment, proof_for_challenge, challenge, settings.q,
                                                                             settings.h1, settings.h2, settings.Modulus_N, settings.paillier_public_key.n,
                                                                               settings.paillier_public_key.g, settings.c1, settings.c2)
        
        if not alice_approves_bob_proof_result:
            raise ValueError("Bob failed ZK proof!")

        decrypted_value = self.decrypt_value(enc_result)
        alpha = decrypted_value % self.q
        return alpha  # Alice holds α only

    def bob_finalize(self, beta_prime):
        """Bob computes β = his additive share of ab """
        beta = (-beta_prime) % self.q  # Mod q assumption
        return beta  # Bob holds β only



q = 13
N = q ** 8  #Modulus
m = 11
h1 = 13
h2 = 23
# Alice's secret
a = 11

# Bob's secret
b = 73

# Example run
mta = MTAProtocolWithZKP(q, N, h1, h2, N, h1, h2, a, b)  #For example both Alice and Bob having the same Paillier Keys and


# Protocol execution
enc_a, pub_key, commitment_of_a = mta.alice_encrypting_a_and_sending_commitment(a)
bob_challenges_alice = mta.bob_challenging_a_commitment(pub_key, commitment_of_a)
proof_for_challenge = mta.alice_sends_proof_answering_challenge(commitment_of_a, a, bob_challenges_alice)
enc_result, beta_prime, bob_commitment = mta.bob_verify_a_commiting_encrypting_b(enc_a, pub_key, bob_challenges_alice,proof_for_challenge,commitment_of_a, b)
alice_challenges_bob = mta.alice_challenging_a_commitment(mta.Bob_Alg_Settings.paillier_public_key, bob_commitment)
alpha = mta.alice_finalize(enc_result, bob_commitment, pub_key, b, beta_prime)
beta = mta.bob_finalize(beta_prime)

# Verify correctness
assert (alpha + beta) % 10**6 == (a * b) % 10**6
print(f"Alice's share: {alpha}, Bob's share: {beta}")
