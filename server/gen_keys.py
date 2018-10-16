from crypto import OAEP

cipher = OAEP()

try: 
	with open('private.pem', 'r') as f:
		private_key = f.read()
	with open('public.pem', 'r') as f:
		public_key = f.read()
except:
	private, public = cipher.generate_keys()
	with open('public.pem','wb') as f:
		f.write(public.exportKey())
	with open('private.pem','wb') as f:
		f.write(private.exportKey())