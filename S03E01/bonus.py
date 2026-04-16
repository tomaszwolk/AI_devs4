from pathlib import Path

bad_sensors = [
    '0158', '0307', '0516', '0567', '0753', '1053', '1269', '1632', '1678',
    '1743', '1819', '2044', '2175', '2238', '2500', '2958', '3123', '3713',
    '3798', '4040', '4186', '4237', '4630', '4673', '4888', '5000', '5022',
    '5156', '5405', '5714', '5715', '5799', '6197', '6281', '6336', '7266',
    '7680', '7701', '8076', '8168', '8369', '8410', '8457', '9151', '9288',
    '9422', '9518', '9583', '9604', '9614', '9717', '9848'
]

bonus_sensors = [
    '9132', '1522', '2306', '1048', '2119'
]

special_sensors = [
    '2137'
]
# Podaj ścieżkę do folderu z wypakowanymi jsonami
sensors_dir = Path(__file__).parent / "data" / "sensors"
for sensor_id in special_sensors:
    # Doklejamy .json do ID z Twojej listy
    filename = f"{sensor_id}.json"
    filepath = sensors_dir / filename

    # Zabezpieczenie na wypadek, gdyby plik nie istniał
    if not filepath.exists():
        print(f"Brak pliku: {filepath}")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

        # JSON z czujnika powinien mieć minimum 9 linijek
        if len(lines) < 9:
            continue

        # Linijka 3 (indeks 2) - wyciągamy pierwsze 4 znaki klucza "timestamp"
        line_3 = lines[2]
        parts_3 = line_3.split('"')
        if len(parts_3) >= 3:
            a = parts_3[1][:4]  # Powinno dać 'time'
        else:
            continue

        # Linijka 9 (indeks 8) - wyciągamy znaki z notatki operatora
        line_9 = lines[8]
        parts_9 = line_9.split('"')

        if len(parts_9) >= 4:
            s = parts_9[3]  # Zmienna 's' to nasza notatka

            # Notatka musi mieć co najmniej 76 znaków,
            # żeby wyciągnąć literę z 76. pozycji!
            if len(s) >= 76:
                # Pamiętaj: AWK liczy od 1, Python od 0
                # (więc -1 do każdego indeksu)
                b = s[43] + s[59] + s[65] + s[73] + s[75]

                flag = f"{{FLG:{a.upper()}{b.upper()}}}"

                print(f"Plik {filename}: {flag} | Notatka: {s[:30]}...")
