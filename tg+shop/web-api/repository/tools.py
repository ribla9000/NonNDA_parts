import base64
import hashlib
import os
import ecdsa


def get_values(values):
    if values is None:
        return None
    return [dict(value) for value in values] if isinstance(values, list) else dict(values)


def validate_pub_key(pub_key: str, x_sign: str, body: bytes):
    pub_key_base64 = pub_key
    x_sign_base64 = x_sign
    pub_key_bytes = base64.b64decode(pub_key_base64)
    signature_bytes = base64.b64decode(x_sign_base64)
    pub_key = ecdsa.VerifyingKey.from_pem(pub_key_bytes.decode())

    ok = pub_key.verify(signature_bytes, body, sigdecode=ecdsa.util.sigdecode_der, hashfunc=hashlib.sha256)
    return ok


def rewrite_env(key: str, value: str):

    with open('.env', 'r') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        if lines[i].startswith(key + "="):
            lines[i] = key + "=" + f"'{value}'" + "\n"
            print(lines[i])
            break

    with open('.env', 'w') as file:
        file.writelines(lines)

    os.environ[key] = value