import hashlib

def generate_token(data):
    """Veriden bir token üretir (SHA256 hash)."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# Örnek token'lar oluşturma
token1 = "gurkan_yilmaz_lisans_1"
token2 = "deneme_token_2025"

hashed_token1 = generate_token(token1)
hashed_token2 = generate_token(token2)

print(f"'{token1}' için hashlenmiş token: {hashed_token1}")
print(f"'{token2}' için hashlenmiş token: {hashed_token2}")

# Bu çıktıları kopyalayıp tokens.txt dosyasına yapıştırın.
# Örnek:
# tokens.txt içeriği:
# d7a6f8e... (hashed_token1)
# a1b2c3d... (hashed_token2)
