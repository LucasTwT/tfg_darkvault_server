from passlib.context import CryptContext

auth_key_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
