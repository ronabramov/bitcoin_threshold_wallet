import bcrypt
import random
import gmpy2
import sympy
from models.models import user_modulus


def hash_password(password: str) -> str:
    """Hash the password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_matrix_user(email : str, user_name : str, password: str):
    #Here we should take the user to the element's UI, to follow registration process. Finally we would need to save the username
    #Place holder for connecting new user
    return (user_name,password)

def pick_element_from_Multiplicative_group(N):
    if N <= 1:
        raise ValueError("N must be greater than 1.")
    
    while True:
        a = random.randint(1, N - 1)
        if gmpy2.gcd(a, N) == 1:
            return a

def generate_user_modulus_parameters():
    N = generate_rsa_modulus()[0]
    h1 = random.randint(2, N-1)
    h2 = random.randint(2,N-1)
    return user_modulus(N=N, h1=h1, h2=h2)

def generate_safe_prime(bits=1024):
    """Generates a safe prime p where p = 2p' + 1 and p' is prime."""
    while True:
        p_prime = sympy.randprime(2**(bits-1), 2**bits)
        p = 2 * p_prime + 1
        if sympy.isprime(p):
            return p

def generate_rsa_modulus():
    """Generates the RSA modulus N_i = P * Q where P and Q are safe primes."""
    p = generate_safe_prime()
    q = generate_safe_prime()
    N = p * q
    return N, p, q

    