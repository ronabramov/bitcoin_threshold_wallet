from enum import Enum

"""
Algorithm Stages - From Player Pi perspective:
1. Key Generation protocol - Player Pi run VSS protocl on his randomized key u_i in Z_q
2. Signature Phase one - Player Pi creates shrinked (t,t+1) share of his key share, w_i.
   Choose u.a.r k_i, gamma_i and broadcast commitment of g^(gamma_i)
3. Signature Phase two - Player Pi run Mta Protocol with every other player, generating shares delta_i of k*gamma
   In addition, running MtaWc Algorithm with every other player, generating shares sigma_i for k*w.
4. Signature Phase three - Player Pi sends delta_i in the channel. when delta_j arrived from every other participant, calculate delta^(-1)
5. Signature Pahse four - Pi sends decommitment of g^(gamma_i) [For commitment from step 2], and Schnor ZK proof for knowing gamma_i.
   Compute R = (Prod_{j in S}  (g^(gamma_j))^(delta^-1)) and r = H'(R)
6. Signature Pahse five - Player Pi sets s_i = m*k_i + r*sgima_i, chose u.a.r l_i, rho_i from Z_q and compute V_i = R^(s_i)*g^(l_i) , A_i = g^(rho_i).
   P_i send commitment for (V_i, A_i), along with Schnor ZK proof for knowing s_i, l_i, rho_i.
   If any of the arrived ZK Proofs fail - Pi ABORTS.
   Pi calculates A = prod_{i in S} A_i , along with V=g^(-m)* y^(-r) * (prod_{i in S}V_i)
7. Signature Pahse six - Player Pi computes U_i = V^(rho_i) , T_i = A^(l_i). Then sending commitment for (U_i, T_i).
   Once everyone else sent their commitment for U_i, T_i, sending decommitment for U_i and T_i.
   Check if prod_{i in S} T_i == prod_{i in S} U_i. If not, ABORT.
   Pi broadcasts s_i. When all other s_j arrived, calculate s= sum_{j in S} s_j. 
8. Signature Pahse seven - Verify that (r,s) is a valid signature. If so, accept.
"""


class Algorithm_Step(str, Enum):
    KEY_GENERATION_PROTOCOL = "key_generation_protocol"
    SIGNATURE_PHASE_ONE = "signature_phase_one"
    SIGNATURE_PHASE_TWO = "signature_phase_two"
    SIGNATURE_PHASE_THREE = "signature_phase_three"
    SIGNATURE_PHASE_FOUR = "signature_phase_four"
    SIGNATURE_PHASE_FIVE = "signature_phase_five"
    SIGNATURE_PHASE_SIX = "signature_phase_six"
    SIGNATURE_PHASE_SEVEN = "signature_phase_seven"
    
