import base64
import hashlib
s = "this is a test string"
print(s.encode(encoding="utf-8"))
print([bin(x) for x in list(s.encode(encoding="utf-8"))])
e = base64.b64encode(s.encode(encoding="utf-8"))
print(e)
print(base64.b64decode(e).decode(encoding="utf-8"))

url = "www.sohu.com"
print(url.encode())
print(hashlib.sha256(url.encode()))
print(hashlib.sha256(url.encode()).hexdigest())
print(hashlib.sha256(url.encode()).hexdigest()[:6])

raw = hashlib.sha256(url.encode()).hexdigest().encode()[:6]
print(raw)                       
print(base64.urlsafe_b64encode(raw).decode()[:8])

raw2 = hashlib.sha256(url.encode()).hexdigest()[:6]
print(raw2)

print(hash((raw, raw2)))