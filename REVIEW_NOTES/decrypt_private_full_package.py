#!/usr/bin/env python3
import sys
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

meta = json.load(open('REVIEW_NOTES/PRIVATE_FULL_METADATA_20251224.json'))
salt = base64.b64decode(meta['salt_b64'])
iterations = meta['iterations']
enc_file = Path('REVIEW_NOTES') / meta['encrypted_file']
plain_zip = meta['plaintext_zip']

if len(sys.argv) < 2:
    print('Usage: decrypt_private_full_package.py <passphrase>')
    sys.exit(1)
passphrase = sys.argv[1].encode('utf-8')

kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
key = base64.urlsafe_b64encode(kdf.derive(passphrase))
fernet = Fernet(key)
enc = open(enc_file, 'rb').read()
try:
    dec = fernet.decrypt(enc)
    out = Path('REVIEW_NOTES') / plain_zip
    open(out, 'wb').write(dec)
    print('Decrypted to', out)
except Exception as e:
    print('Decryption failed:', e)
