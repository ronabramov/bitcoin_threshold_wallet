from functools import reduce

class ShareShrinker:
    """
    Algorithm for transforming locally (t,n) share into (t,t+1) share of the same secret.
    S - list of participating indecis 
    q - Field of the original Shamir Polynomial
    i - index of user share
    x_i - user share (evaluation of original polynomial)
    Output: w_i = Additive (t,t+1) share of x
    """
    def __init__(self, q : int, i : int, x_i : int, S : list):
        self.q = q
        self.i = i
        self.x_i = x_i
        self.S = S

    def mod_inverse(self, a, q) -> int:
        """ Compute modular inverse of a mod q using Fermat's theorem"""
        return pow(a, q - 2, q)  # a^(q-2) mod q

    def compute_lagrange_coefficient(self, i, S, q) -> int:
        """ Compute Lagrange coefficient λ_{i,S} in Z_q. """
        numerator = reduce(lambda acc, j: (acc * j) % q, (j for j in S if j != i), 1)
        denominator = reduce(lambda acc, j: (acc * (j - i)) % q, (j for j in S if j != i), 1)
        
        return (numerator * self.mod_inverse(denominator, q)) % q

    def compute_new_share(self) -> int:
        """ Compute the transformed share w_i = λ_{i,S} * x_i in Z_q. """
        lambda_i_S = self.compute_lagrange_coefficient(self.i, self.S, self.q)
        return (lambda_i_S * self.x_i) % self.q

# Example usage
# S = {1, 2, 3, 4}  # Example set of t+1 indices
# x_i = 123  # Example secret share
# i = 2  # The index of the participant whose new share we want
# q = 7919  # Example prime field (large enough for security)
# shrinker = ShareShrinker(q=q,i=i,x_i=x_i,S=S)
# w_i = shrinker.compute_new_share()
# print(f"New share w_{i} in Z_{q} = {w_i}")
