import base64
import gzip

# Dane pobrane przez Ciebie, ułożone od najmłodszego (2000) do najstarszego (1976)
data_parts = [
    "H4sIEMggzmkA/yAgIENoeWJhIHN", # mrocznymsciciel69 (2000)
    "pZSBjb3MgemxlIHpkZWtvZG93YW", # sergouda (1998)
    "xvIHRlbXUgYmVqc3UuLi4gaSBjY", # zwyklysernik (1996)
    "Wx5IG1pc3Rlcm55IHBsYW4uLi4g", # aleurwal (1994)
    "IAAFQDEKwjAU3f8pnqOLB+hWpZa", # bezloginu (1992)
    "COImD2zf9avSbSBoRKi6Chygunk", # nocnykebab (1990)
    "OcpLlXKQPHq7I5yoRo41i5TU9J7", # lubieplacki (1988)
    "/+nkVOQ6PoXdsr7vhsR5diG9mzh", # kosmicznypaczek (1985)
    "HWd0ny/KbF1Ni7wslqsHUVWnL2o", # glodnywombat (1982)
    "PIy4GVguLizeHGysa23eIkn5wjJ", # wujekbagieta (1979)
    "kNRgXZeAAuN6q3fAAAAA=="        # lordkalafior (1976)
]

# 1. Łączymy w jeden długi ciąg Base64
full_b64 = "".join(data_parts)

# 2. Dekodujemy Base64 do bajtów
compressed_data = base64.b64decode(full_b64)

# 3. Rozpakowujemy Gzip
try:
    result = gzip.decompress(compressed_data)
    print("Zdekodowana wiadomość:")
    print(result.decode('utf-8'))
except Exception as e:
    print(f"Błąd dekompresji: {e}")
    # Jeśli dekompresja zawiedzie, wypisz surowe bajty, by sprawdzić co jest w środku
    print(compressed_data)



"H4sIEMggzmkA/yAgIENoeWJhIHNpZSBjb3MgemxlIHpkZWtvZG93YWxvIHRlbXUgYmVqc3UuLi4gaSBjYWx5IG1pc3Rlcm55IHBsYW4uLi4gIAAFQDEKwjAU3f8pnqOLB+hWpZaCOImD2zf9avSbSBoRKi6ChygunkOcpLlXKQPHq7I5yoRo41i5TU9J7/+nkVOQ6PoXdsr7vhsR5diG9mzhHWd0ny/KbF1Ni7wslqsHUVWnL2oPIy4GVguLizeHGysa23eIkn5wjJkNRgXZeAAuN6q3fAAAAA==