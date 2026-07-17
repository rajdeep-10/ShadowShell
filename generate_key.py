from cryptography.fernet import Fernet

# Generate a key and save it to a file for the server and agent to share
key = Fernet.generate_key()

with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("[+] Encryption key generated and saved to secret.key")
print("Key:", key.decode())
