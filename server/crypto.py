import base64
import hashlib
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from ast import literal_eval

class OAEP():
	def generate_keys(self):
		random_number_generator = Random.new().read
		key = RSA.generate(2048, random_number_generator)
		private_key, public_key = key, key.publickey()
		return [private_key, public_key]

	def decrypt(self, ciphertext: str, private_key: str) -> str:
		ciphertext = base64.b64decode(ciphertext)
		oaep_key = PKCS1_OAEP.new(private_key)
		plaintext = oaep_key.decrypt(literal_eval(str(ciphertext)))
		return plaintext.decode('utf-8')

	def encrypt(self, plaintext: str, public_key: str) -> str:
		oaep_key = PKCS1_OAEP.new(public_key)
		ciphertext = oaep_key.encrypt(self._encode_plaintext(plaintext))
		return base64.b64encode(ciphertext)

	def _encode_plaintext(self, text: str) -> str:
		if isinstance(text, int) or isinstance(text, float):
			text = str(text)
		return text.encode('utf-8')
		

class AESCipher():
    def __init__(self, key): 
        self.block_size = 16
        self.key = hashlib.sha256(key.encode()).digest()

    def decrypt(self, ciphertext: str) -> str:
        ciphertext = base64.b64decode(ciphertext)
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(ciphertext[AES.block_size:])).decode('utf-8')

    def encrypt(self, plaintext: str) -> str:
        plaintext = self._pad(plaintext)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(plaintext))

    def _pad(self, text: str) -> str:
        if isinstance(text, int) or isinstance(text, float):
        	text = str(text)
        return bytes(text+(self.block_size-len(text)%self.block_size)* \
        	chr(self.block_size-len(text)%self.block_size), encoding=('utf-8'))

    def _unpad(self, text: str) -> str:
        return text[:-ord(text[len(text)-1:])]