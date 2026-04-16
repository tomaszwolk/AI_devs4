import sys
import logging
from config import MAIN_MODEL, MAIN_SYSTEM_PROMPT
from agent import MainAgent

logger = logging.getLogger(__name__)


def main():
    agent = MainAgent(model=MAIN_MODEL, system_prompt=MAIN_SYSTEM_PROMPT)

    user_prompt = ("""
        Oto Twoje zadania. Wykonaj je rygorystycznie, używając narzędzia call_oko_editor_api.
        TWOJE NAJWAŻNIEJSZE ZADANIE: Musisz użyć DOKŁADNIE takich tekstów (title i content), jakie podałem poniżej. Nie zmieniaj ani jednego słowa, po prostu skopiuj te wartości do wywołania narzędzia. Przekazuj title i content w każdym zapytaniu.

        KROK 1: Aktualizacja Incydentu Skolwin
        - page: "incydenty"
        - record_id: "380792b2c86d9c5be670b3bde48e187b"
        - action: "update"
        - title: "MOVE04 Trudne do klasyfikacji ruchy nieopodal miasta Skolwin"
        - content: "Czujniki zarejestrowały szybko poruszający się obiekt, który zmierzał w kierunku rzeki. Zidentyfikowano, że obiekt to zwierzęta, a dokładniej bobry. Alarm okazał się fałszywy. W mieście Skolwin nie przebywają ludzie ani pojazdy. Nie należy wysyłać niszczycieli."

        KROK 2: Aktualizacja Zadania Skolwin
        - page: "zadania"
        - record_id: "380792b2c86d9c5be670b3bde48e187b"
        - action: "update"
        - is_done: "YES"
        - title: "Zbadanie nagrań z okolic Skolwina"
        - content: "Próbki ruchu zarejestrowane w okolicach miasta Skolwin zostały skorelowane z nagraniami satelitarnymi. Potwierdzono, że widziano tam wyłącznie zwierzęta, np. bobry. Brak obecności ludzi i pojazdów."

        KROK 3: Stworzenie Incydentu Komarowo (nadpisanie Domatowa)
        - page: "incydenty"
        - record_id: "ff3313a39099222e325f03b378680e3c"
        - action: "update"
        - title: "MOVE01 Raport o wykryciu ruchu ludzi w okolicach miasta Komarowo"
        - content: "Wykryto ruch ludzi w okolicach miasta Komarowo. Zapisy z radarów wskazują na wzmożoną aktywność i przemieszczanie się jednostek pieszych. Konieczne jest przekierowanie uwagi operatorów na to niezamieszkałe miasto i natychmiastowe wysłanie tam patroli."

        KROK 4: Weryfikacja
        - Po wykonaniu kroków 1-3 zadzwoń do API z action="done". Zwróci Ci to flagę.
    """).strip()

    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
