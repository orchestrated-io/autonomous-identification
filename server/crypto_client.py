import sys
import json
import binascii
import random, string
import requests
from Crypto.PublicKey import RSA
from crypto import AESCipher, OAEP
from hash_constructor import construct_tuples, generate_hash


MAX_SIZE = 2048
MAX_SNIPPETS = 4

#in production the entropy file will be located elsewhere
try:
	with open('info2048.bin','r') as f:
		entropy_data = f.read()
except FileNotFoundError:
	print('Cannot read entropy file. Aborting.')
	sys.exit(1)

#in production the public key may be located elsewhere
try:
	with open('public.pem', 'r') as f:
		public_key = f.read()
		public_key = RSA.importKey(public_key)
except:
	print('Cannot read public key file. Aborting.')
	sys.exit(1)

def hex2bin(hex_str: str) -> str:
    return binascii.unhexlify(hex_str)

def bin2hex(bin_str: str) -> str:
    return binascii.hexlify(bin_str)

def rand_string() -> str:
	return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))

def send_payload(url, encrypted_key: bytes, aes_payload: bytes) -> object:
	encrypted_key = bin2hex(encrypted_key).decode('utf-8')
	aes_payload = bin2hex(aes_payload).decode('utf-8')
	payload = {
	    'data': encrypted_key, 
	    'payload': aes_payload
	}
	payload=json.dumps(payload)
	headers = {'content-type': 'application/json'}
	return requests.post(url, data=payload, headers = headers)

def generate_hashval(text: str, data: str, max_size: int) -> str:
	return generate_hash(text, data, max_size)


def get_credentials(url, credential_source) -> str:
	rsa = OAEP()
	key = rand_string()

	encrypted_key = rsa.encrypt(key,public_key)
	crypto = AESCipher(key)
	intervals = construct_tuples(MAX_SNIPPETS, MAX_SIZE)
	hashval = generate_hashval(intervals, entropy_data, MAX_SIZE)

	interval_payload = {
		'hashval': hashval,
		'intervals': intervals,
		'credential_source': credential_source
	}
	aes_interval=json.dumps(interval_payload)
	aes_payload = crypto.encrypt(aes_interval)

	response = send_payload(url, encrypted_key, aes_payload)
	if response.status_code == 201:
		rdict = json.loads(response.text)
		response = hex2bin(rdict['message'].encode('utf-8'))
		plaintext = crypto.decrypt(response)
		return(plaintext)
	else:
		return ''.join(['An error occurred', str(response.status_code), response.text])


if __name__ == '__main__':
	try:
		result = get_credentials(sys.argv[1], sys.argv[2])
		print(result)
	except ValueError:
		print('Use: {0} {1} {2}'.format(sys.argv[0], sys.argv[1], sys.argv[2]))
		sys.exit(1)
