from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a password using Argon2.
    """
    return pwd_context.hash(password)