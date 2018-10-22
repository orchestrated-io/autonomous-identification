from crypto import AESCipher, OAEP
from Crypto.PublicKey import RSA
import binascii
import random, string
import sys
import requests
import json
import hashlib
from random import randint

MAX_SIZE = 2048
MAX_SNIPPETS = 4

#in production the entropy file will be located elsewhere
with open('info2048.bin','r') as f:
	data = f.read()

def hex2bin(hexStr):
    return binascii.unhexlify(hexStr)

def bin2hex(binStr):
    return binascii.hexlify(binStr)

def rand_string():
	return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))

try:
	#in production the public key may be located elsewhere
	with open('public.pem', 'r') as f:
		public_key = f.read()
		public_key = RSA.importKey(public_key)
except:
	print('Cannot read public key file. Aborting.')
	sys.exit(1)

rsa = OAEP()
key = rand_string()

def construct_tuples():
	tuples = []
	for i in range(MAX_SNIPPETS):
		snippet_tuple = get_random_tuple()
		tuple_vals = (',').join([str(x) for x in snippet_tuple])
		tuples.append(tuple_vals)
	string_tuples = ('|').join(tuples)
	return string_tuples

def get_random_tuple():
	first_num, second_num = 0,0
	while first_num == second_num:
		first_num = randint(0,MAX_SIZE-1)
		second_num = randint(0,MAX_SIZE-1)
		line_number = randint(0,MAX_SIZE-1)
	return (first_num, second_num, line_number)

def get_snippet(data, first_num, second_num, line_number):
	offset = MAX_SIZE*line_number
	first_num += offset
	second_num += offset
	if first_num < second_num:
		text_slice = data[first_num:second_num]
	else:
		text_slice = data[second_num:first_num]
	return text_slice

def send_payload(url, encrypted_key, aes_payload):
	encrypted_key = bin2hex(encrypted_key).decode('utf-8')
	aes_payload = bin2hex(aes_payload).decode('utf-8')
	payload = {
	    'data': encrypted_key, 
	    'payload': aes_payload
	}
	payload=json.dumps(payload)
	headers = {'content-type': 'application/json'}

	r = requests.post(url, data=payload, headers = headers)
	return r

def generate_hashval(text):
	tuples = text.split('|')
	hash_strings = []
	for item in tuples:
		tuple_array = item.split(',')
		tuple_array = [int(x) for x in tuple_array]
		snippet = get_snippet(data, *tuple_array)
		hash_strings.append(snippet)
	prehashval = ('').join(hash_strings)
	hashval = hashlib.sha256(prehashval.encode('utf-8')).hexdigest()
	return hashval

def get_credentials(url, credential_source):
	encrypted_key = rsa.encrypt(key,public_key)
	crypto = AESCipher(key)
	intervals = construct_tuples()
	hashval = generate_hashval(intervals)

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
		return((' ').join(['An error occurred', str(response.status_code), response.text]))
