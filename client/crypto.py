import six
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

    def _encode_plaintext(self, text):
        if isinstance(text, int):
            return six.binary_type(text)
        for string_type in six.string_types:
            if isinstance(text, string_type):
                return text.encode('utf8')
        if isinstance(text, six.binary_type):
            return text

    def encrypt(self, plaintext, public_key):
        oaep_key = PKCS1_OAEP.new(public_key)
        ciphertext = oaep_key.encrypt(self._encode_plaintext(plaintext))
        return base64.b64encode(ciphertext)
        return ciphertext

    def decrypt(self, ciphertext, private_key):
        ciphertext = base64.b64decode(ciphertext)
        oaep_key = PKCS1_OAEP.new(private_key)
        plaintext = oaep_key.decrypt(literal_eval(str(ciphertext)))
        return six.text_type(plaintext, encoding='utf8')


class AESCipher():
    def __init__(self, key): 
        self.block_size = 16
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, plaintext):
        plaintext = self._pad(plaintext)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(plaintext))

    def decrypt(self, ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(ciphertext[AES.block_size:])).decode('utf-8')

    def _pad(self, text):
        return bytes(text+(self.block_size-len(text)%self.block_size)*chr(self.block_size-len(text) % self.block_size), encoding=('utf-8'))

    def _unpad(self, text):
        return text[:-ord(text[len(text)-1:])]