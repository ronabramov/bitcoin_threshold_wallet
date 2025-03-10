from local_db.sql_db import Transaction, Wallet
from ecdsa.curves import curve_by_name
from ecdsa.ellipticcurve import PointJacobi
from common_utils import H


class SignatureVerifier:
    def verifySignatureIsValid(transaction : Transaction, r : int, s : int, y): 
        #RON TODO : what y is? 
        M = Transaction.model_dump_json() #Ron/ Gilad TODO : implement
        m = H(M)
        wallet : Wallet = transaction.wallet 
        curve =  curve_by_name(wallet.curve_name)
        g = curve.generator
        s_inv = pow(s, -1, curve.order)
        R_prime : PointJacobi = g * ((m * s_inv)% curve.order) * y *((r * s_inv) % curve.order) 
        H_R_Prime = R_prime.x() % curve.order
        return H_R_Prime == r