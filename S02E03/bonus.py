import tiktoken
from tools import create_payload, send_payload

enc = tiktoken.encoding_for_model("gpt-5")


def generate_exact_tokens(target_length: int) -> str:
    """Generuje tekst o DOKŁADNIE podanej liczbie tokenów."""
    # " error" (ze spacją) to zawsze 1 token w GPT-4
    text = " error\n" * target_length

    # Podwójne sprawdzenie dla pewności
    tokens = enc.encode(text)
    if len(tokens) != target_length:
        text = enc.decode(tokens[:target_length])

    assert len(enc.encode(text)) == target_length
    return text


# ASCII dla F, L, A, G
target_tokens = [70, 76, 65, 71]

for t in target_tokens:
    logs = generate_exact_tokens(t)
    # logs = "g\n\n\n\nm\n\n\n\nb\n\n\n\nh\n\n\n\n" + ("\n" * 20)
    payload = create_payload(logs)
    print(f"\n[>] Wysyłam request o długości dokładnie {t} tokenów (Znak '{chr(t)}')")
    status_code, response = send_payload(payload)
    print(f"Status code: {status_code}")
    print(f"[<] Odpowiedź serwera: {response}")
