from phe import paillier


class Bob_ZKProof_RegMta_ProverCommitment:
    def __init__(self, alpha, rho, rho_prime, sigma, beta, gamma, tau, z, z_prime, t, v, w):
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.rho_prime = rho_prime
        self.sigma = sigma
        self.gamma= gamma
        self.tau = tau
        self.z = z
        self.z_prime = z_prime
        self.t = t
        self.v = v
        self.w = w


class Bob_ZKProof_RegMta_Proof_For_Challenge:
    def __init__(self, s, s1, s2, t1, t2):
        self.s = s
        self.s1 = s1
        self.s2 = s2
        self.t1 = t1
        self.t2 = t2


class Bob_ZKProof_RegMta_Settings:
    def __init__(self, q, public_key : paillier.PaillierPublicKey, Modulus_N, h1, h2, c1, c2):
        # This is mainly data that the prover holds. 
        # We might prefer having settings for prover and settings for verifier
        self.q = q
        self.paillier_public_key = public_key
        self.Modulus_N = Modulus_N
        self.h1 = h1
        self.h2 = h2
        self.c1 = c1
        self.c2 = c2
        

class Bob_ZKProof_RegMta_Prover_Settings(Bob_ZKProof_RegMta_Settings):
    def __init__(self, q, public_key, Modulus_N, h1, h2, b, beta_prime, r, c1, c2):
        super().__init__(q, public_key, Modulus_N, h1, h2, c1, c2)
        self.r = r
        self.beta_prime = beta_prime
        self.b = b