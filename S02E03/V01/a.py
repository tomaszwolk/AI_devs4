import re
from pathlib import Path

def extract_uppercase_words(file_path):
    # Regex: \b oznacza granicę słowa, [A-Z0-9]{2,} oznacza 2 lub więcej znaków (duże litery/cyfry)
    word_pattern = re.compile(r'\b[A-Z0-9]{2,}\b')
    found_words = set()

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # findall zwraca listę wszystkich dopasowań w linii
            words = word_pattern.findall(line)
            for word in words:
                found_words.add(word)
                
    return found_words

log_path = Path(__file__).parent / "data" / "failure.log.txt"
unique_words = extract_uppercase_words(log_path)
print(sorted(list(unique_words)))