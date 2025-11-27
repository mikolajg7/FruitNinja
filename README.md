# 🥷🍎 Fruit Ninja CV (Computer Vision)

**Fruit Ninja CV** to interaktywna gra zręcznościowa sterowana gestami dłoni, wykorzystująca kamerę internetową. Projekt łączy klasyczną mechanikę przecinania owoców z nowoczesną technologią wizji komputerowej (OpenCV + MediaPipe) oraz silnikiem gier (PyGame).

## 🚀 Możliwości

* **Sterowanie ruchem:** Graj używając własnych dłoni (obsługa Multitouch - obie ręce naraz!).
* **Dwa Tryby Gry:**
    * **Arcade:** Klasyczna rozgrywka na życia. Unikaj bomb!
    * **Time Attack:** 60 sekund na zdobycie jak największej liczby punktów.
* **Dynamiczna Trudność:** Gra przyspiesza z czasem, zwiększając tempo i ilość obiektów (tryb Chaos).
* **Zaawansowana Fizyka:** Owoce rozpadają się na kawałki po przecięciu, posiadają grawitację i pęd.
* **Lokalny Ranking:** Zapisywanie najlepszych wyników (Top 10) dla każdego trybu osobno.
* **Nowoczesne UI:** Interaktywne menu, animowane przyciski i płynne przejścia.
* **Fullscreen:** Gra automatycznie skaluje się do pełnego ekranu.

## 🛠️ Technologie

Projekt został napisany w języku **Python 3.10+** i korzysta z następujących bibliotek:

* **OpenCV (`cv2`):** Obsługa kamery i przetwarzanie obrazu.
* **MediaPipe:** Zaawansowana detekcja dłoni i palców w czasie rzeczywistym.
* **PyGame:** Silnik graficzny, renderowanie UI, obsługa dźwięku i fizyki 2D.
* **NumPy:** Obliczenia macierzowe dla transformacji obrazu.

## 📦 Instalacja (z użyciem uv)

Ten projekt zaleca używanie **uv** – ultra-szybkiego menedżera pakietów dla Pythona.

1.  **Zainstaluj uv** (jeśli jeszcze nie masz):
    * **Windows (PowerShell):**
        ```powershell
        powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
        ```
    * **macOS / Linux:**
        ```bash
        curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
        ```
    * *Alternatywnie (jeśli masz już Pythona):* `pip install uv`

2.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/twoj-nick/fruit-ninja-cv.git](https://github.com/twoj-nick/fruit-ninja-cv.git)
    cd fruit-ninja-cv
    ```

3.  **Stwórz środowisko i zainstaluj biblioteki:**
    Komenda ta automatycznie utworzy folder `.venv` i zainstaluje w nim pakiety.
    ```bash
    uv venv
    uv sync
    ```

4.  **Uruchom grę:**
    Dzięki `uv run` nie musisz ręcznie aktywować środowiska wirtualnego.
    ```bash
    uv run run.py
    ```

## 🎮 Jak grać?

1.  Upewnij się, że masz podłączoną kamerę internetową i dobre oświetlenie.
2.  Stań w odległości 1-2 metrów od kamery.
3.  Twoje dłonie to miecze!
    * **Palec wskazujący** steruje kursorem (zielona kropka).
    * **Przecinaj owoce**, aby zdobywać punkty.
    * **Unikaj bomb!** (W trybie Arcade tracisz życie, w Time Attack tracisz punkty).
4.  W menu sterujesz, najeżdżając dłonią na przyciski i przytrzymując je przez chwilę.

## ⚙️ Konfiguracja

Możesz dostosować parametry gry (trudność, kolory, czułość kamery) edytując plik:
`src/config.py`

## 📜 Licencja
Ten projekt został stworzony w celach edukacyjnych. Wykorzystuje bibliotekę MediaPipe (Google), PyGame, Font Gang of Three i darmowe assety graficzne dla owoców oraz bomb.