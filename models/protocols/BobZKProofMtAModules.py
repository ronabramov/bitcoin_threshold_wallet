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