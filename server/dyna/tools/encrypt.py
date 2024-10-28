from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import base64

def derive_key(password: str, salt: bytes) -> bytes:
    """Tạo khóa từ mật khẩu bằng cách sử dụng scrypt."""
    return scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)

def encrypt(message: str, password: str) -> str:
    """Mã hóa thông điệp bằng AES."""
    salt = get_random_bytes(16)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return base64.b64encode(salt + cipher.nonce + tag + ciphertext).decode()

def decrypt(encrypted_message: str, password: str) -> str:
    """Giải mã thông điệp bằng AES."""
    data = base64.b64decode(encrypted_message.encode())
    salt = data[:16]
    nonce = data[16:32]
    tag = data[32:48]
    ciphertext = data[48:]
    
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted_message.decode()