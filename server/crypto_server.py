import sys
import json
import binascii
from Crypto.PublicKey import RSA
from crypto import AESCipher, OAEP
from file_utilities import read_s3, input_path
from credential_store import retrieve_credentials
from hash_constructor import generate_hash

MAX_SNIPPETS = 4
MAX_SIZE = 2048

try:
	entropy_data = read_s3(input_path(), 'info2048.bin')
except FileNotFoundError:
	print('Cannot read entropy file. Aborting.')
	sys.exit(1)

try:
	priv_key = read_s3(input_path(), 'private.pem')
	private_key = RSA.importKey(priv_key)
except FileNotFoundError:
	print('Cannot read private key file. Aborting.')
	sys.exit(1)

def hex2bin(hexStr: str) -> str:
    return binascii.unhexlify(hexStr)

def bin2hex(binStr: str) -> str:
    return binascii.hexlify(binStr)

def generate_hashval(text: str, data: str, max_size: int) -> str:
	return generate_hash(text, data, max_size)

def lambda_handler(event: dict, context: dict) -> dict:
	rsa = OAEP()
	payload = event['body']
	client_data = json.loads(payload)
	encrypted_aes_key = hex2bin(client_data['data'].encode('utf-8'))
	aes_key = rsa.decrypt(encrypted_aes_key, private_key)
	cipher = AESCipher(aes_key)

	encrypted_aes_payload = hex2bin(client_data['payload'].encode('utf-8'))
	decrypted_aes_payload = json.loads(cipher.decrypt(encrypted_aes_payload))
	ranges = decrypted_aes_payload['intervals']
	hashval = generate_hashval(ranges, entropy_data, MAX_SIZE)
	received_hashval = decrypted_aes_payload['hashval']

	if received_hashval == hashval:
		credential_source = decrypted_aes_payload['credential_source']
		plaintext = retrieve_credentials(credential_source)
		response = cipher.encrypt(plaintext)
		response = bin2hex(response).decode('utf-8')
		status = 201
	else:
		response = 'not found'
		status = 404
 
	return {
        "statusCode": status,
        "body": json.dumps({
            'message': response
        })
    }