from passlib.hash import des_crypt

# Generate a DES-based hash with salt "HX"
hashed_password = des_crypt.hash("12345", salt="HX")
print(hashed_password)
