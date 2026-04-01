<p align="center"><img width="1868" height="560" src="assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** to aplikacja desktopowa do tworzenia i edycji **teł Game Boy Advance (GBA)**. Umożliwia konwersję obrazów na zestawy kafelków i mapy kafelków kompatybilne z GBA, wizualną edycję kafelków i palet oraz eksport gotowych zasobów do projektów GBA.

> ⚠️ Ta aplikacja jest przeznaczona dla deweloperów, ROM hackerów i pixel artystów, którzy potrzebują precyzyjnej kontroli nad tłami GBA.

---

## 🌐 Tłumaczenia

Ten README jest dostępny w następujących językach:

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Funkcje

- **Konwersja obrazu do GBA**
  - Konwertuje standardowe obrazy na zestawy kafelków i mapy kafelków kompatybilne z GBA.
  - Konfiguruje rozmiar wyjściowy i głębię kolorów (4bpp i 8bpp).
  - Podgląd wyniku przed eksportem.

- **Edycja zestawu kafelków**
  - Wizualny wybór i edycja kafelków.
  - Interaktywne narzędzia rysowania na siatce mapy kafelków.
  - Poziomy powiększenia od 100% do 800% dla edycji piksel po pikselu.

- **Edycja palet**
  - Edycja do 256 kolorów na paletę.
  - Synchronizacja zmian palety z podglądami i kafelkami.
  - Zmiana kolejności, zastępowanie lub dostosowywanie poszczególnych kolorów.

- **Karta podglądu**
  - Wizualizacja wyglądu końcowego tła na ekranie podobnym do GBA.
  - Szybka weryfikacja konfiguracji kafelków i palet.

- **Historia Cofnij/Ponów**
  - Pełne śledzenie historii edycji.
  - Operacje cofania i ponawiania z dużym buforem historii.

- **Konfigurowalny interfejs i pasek stanu**
  - Szczegółowy pasek stanu z wyborem kafelka, współrzędnymi mapy, ID palety, stanem odbicia i poziomem powiększenia.
  - Kontekstowy pasek narzędzi dla każdej karty (podgląd, kafelki, palety).

- **Obsługa wielu języków**
  - Wewnętrzny system tłumaczeń (Translator) z wyborem języka przez ustawienia.
  - Zaprojektowany do obsługi wielu języków w interfejsie.

---

## 🖼️ Zrzuty ekranu

<p align="center"><img width="896" height="590" src="assets/readme/pol_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="1070" height="676" src="assets/readme/pol_preview.png" alt="Image" /></p>

<p align="center"><img width="1070" height="676" src="assets/readme/pol_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="1070" height="676" src="assets/readme/pol_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ Opis architektury

GBA Background Studio jest zbudowany w **Pythonie** i **PySide6**, zgodnie z modularnym projektem interfejsu:

- **Okno główne (`GBABackgroundStudio`)**
  - Zarządza stanem aplikacji (bieżące BPP, poziom powiększenia, wybór kafelka i palety).
  - Zawiera główne karty i niestandardowy pasek stanu.
  - Ładuje i stosuje konfigurację (w tym ostatnią sesję wyjściową).

- **Karty**
  - `PreviewTab` – Podgląd tła w stylu GBA.
  - `EditTilesTab` – Narzędzia do edycji kafelków i mapy kafelków.
  - `EditPalettesTab` – Edytor palet i narzędzia do manipulacji kolorami.

- **Komponenty i narzędzia interfejsu**
  - `MenuBar` – Operacje na plikach (otwieranie obrazu, eksport plików, wyjście) i akcje edytora.
  - `CustomGraphicsView` – Rozszerzony `QGraphicsView` z interakcją opartą na kafelkach.
  - `TilemapUtils` – Wspólna logika interakcji i wyboru mapy kafelków.
  - `HistoryManager` – Zarządzanie cofaniem/ponawianiem dla operacji edytora.
  - `HoverManager`, `GridManager` – Wizualne pomoce dla efektów najechania i nakładek siatki.
  - `Translator`, `ConfigManager` – Lokalizacja i trwała konfiguracja.

---

## 📦 Instalacja

### Wymagania
- **Python** (zalecany 3.12+)
- **Pip** (menedżer pakietów Python)
- **Systemy operacyjne wspierane przez PySide6:**
  - **Windows:** Windows 10 (wersja 1809) lub nowszy.
  - **macOS:** macOS 11 (Big Sur) lub nowszy.
  - **Linux:** nowoczesne dystrybucje z glibc 2.28 lub nowszym.

### Zależności
Główne zależności obejmują:
- `PySide6` (Qt for Python) - *Uwaga: wymaga wersji systemu operacyjnego wymienionych powyżej.*
- `Pillow` (PIL) do przetwarzania obrazów.

Możesz zainstalować zależności za pomocą:
```bash
pip install -r requirements.txt
```

---

### 🏛️ Wsparcie dla starszych systemów (Windows 7 / 8 / 8.1)
Jeśli używasz starszej wersji systemu Windows, która nie obsługuje **PySide6** (interfejsu graficznego), nadal możesz korzystać z silnika konwersji poprzez nasz **Wielojęzyczny Kreator Wiersza Poleceń**.

#### Wymagania
- **Python** (zalecany 3.8+)

Pozwala to na konwersję obrazów na zasoby GBA bez interfejsu graficznego, korzystając z asystenta krok po kroku w Twoim ojczystym języku.

1. Przejdź do katalogu głównego projektu.
2. Uruchom plik **`GBA_Studio_Wizard.bat`**.
3. Wybierz swój język (wsparcie dla 18 języków).
4. Postępuj zgodnie z instrukcjami, aby przeciągnąć obraz i skonfigurować wyjście GBA.

---

## 🚀 Pierwsze kroki

1. **Sklonuj repozytorium**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Utwórz i aktywuj środowisko wirtualne** (opcjonalne, ale zalecane)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # W systemie Windows: .venv\Scripts\activate
   ```

3. **Zainstaluj zależności**

   ```bash
   pip install -r requirements.txt
   ```

4. **Uruchom aplikację**

   ```bash
   python main.py
   ```

---

## 🧭 Podstawowe użytkowanie

1. **Otwieranie obrazu**
   - Przejdź do **Plik → Otwórz obraz** lub naciśnij `Ctrl+O`.
   - Wybierz obraz, który chcesz przekonwertować na tło GBA.

2. **Konfiguracja konwersji**
   - Wybierz **Tryb tła** (**Tryb tekstowy** lub **Tryb rotacji/skalowania**).
   - Wybierz palety lub mapę kafelków do użycia (tylko dla **Trybu tekstowego 4bpp**).
   - Ustaw kolor, który będzie używany jako przezroczysty.
   - Dostosuj rozmiar wyjściowy i inne niezbędne parametry.
   - Kliknij **Konwertuj**, a aplikacja zajmie się resztą.

3. **Edycja kafelków**
   - Przełącz się na kartę **Edytuj kafelki**.
   - Użyj widoku mapy kafelków do rysowania i modyfikowania poszczególnych kafelków.
   - Zaznacz całe obszary, aby kopiować, wycinać, wklejać lub obracać grupy kafelków.
   - Synchronizuj zmiany w czasie rzeczywistym, aby zobaczyć natychmiastowe wyniki.
   - Dostosuj poziom **Zoom** dla doskonałej precyzji.
   - Optymalizuj lub Cofnij optymalizację kafelków, aby zaoszczędzić miejsce lub zapewnić kompatybilność sprzętową.
   - Konwertuj zasoby między formatami **4bpp** i **8bpp**.
   - Płynnie przełączaj między **Trybem tekstowym** a **Trybem rotacji/skalowania**.

4. **Edycja palet**
   - Przejdź do karty **Edytuj palety**.
   - Modyfikuj kolory w siatce palet i dostosowuj je za pomocą edytora kolorów.
   - Zaznacz określone obszary lub wszystkie kafelki należące do palety, aby je zastąpić lub zamienić z inną.

5. **Podgląd tła**
   - Przełącz się na kartę **Podgląd**, aby zobaczyć wierne odwzorowanie wyglądu na prawdziwym GBA.
   - Sprawdź, czy konfiguracje kafelków i palet działają razem doskonale.

6. **Eksport zasobów**
   - Przejdź do **Plik → Eksportuj pliki** lub naciśnij `Ctrl+E`.
   - Eksportuj zestawy kafelków, mapy kafelków i palety w formatach gotowych do integracji z łańcuchem narzędzi deweloperskich GBA.
   - Eksportuj poszczególne zasoby oddzielnie z ich odpowiednich menu, jeśli to konieczne.

---

## 🔄 Cofnij/Ponów

Aplikacja śledzi Twoje działania edycyjne za pomocą **menedżera historii**:

- **Cofnij** – cofa ostatnią operację.
- **Ponów** – ponownie stosuje cofniętą operację.

System historii utrzymuje bufor ostatnich stanów, w tym edycje kafelków, zmiany palet i operacje na mapie kafelków.

---

## ⚙️ Konfiguracja i lokalizacja

### Konfiguracja

Aplikacja używa menedżera konfiguracji do przechowywania ustawień takich jak:

- Ostatnio używany język
- Ostatnio używany poziom powiększenia
- Czy ładować ostatnie wyjście przy uruchomieniu
- Inne preferencje interfejsu i edytora

Konfiguracja jest ładowana przy uruchomieniu i stosowana do interfejsu i menu.

### Lokalizacja

Komponent `Translator` zarządza tekstami interfejsu:

- Domyślny język jest konfigurowany przez ustawienia.
- Pliki tłumaczeń można dodawać lub edytować, aby obsługiwać więcej języków.
- Teksty interfejsu (menu, okna dialogowe, etykiety) przechodzą przez tłumacza.

---

## 🤝 Wkład

Wkład jest mile widziany! Jeśli chcesz pomóc:

1. Zrób fork tego repozytorium.
2. Utwórz gałąź funkcji:
   ```bash
   git checkout -b feature/moja-nowa-funkcja
   ```
3. Zatwierdź swoje zmiany:
   ```bash
   git commit -am "Dodaj moją nową funkcję"
   ```
4. Wypchnij gałąź:
   ```bash
   git push origin feature/moja-nowa-funkcja
   ```
5. Otwórz Pull Request opisujący swoje zmiany.

Proszę utrzymywać kod zgodny z istniejącym stylem i dołączać testy, gdy to możliwe.

---

## 📄 Licencja

Ten projekt jest licencjonowany na podstawie **GNU General Public License v3.0 (GPL-3.0)**.  
Szczegóły znajdziesz w pliku [LICENSE](LICENSE).

---

## 🙏 Podziękowania

- Dziękujemy społecznościom homebrew i ROM hackingu GBA za ich dokumentację i narzędzia.
- Zainspirowany klasycznymi edytorami pixel art i narzędziami deweloperskimi GBA.

---

## 📩 Kontakt i wsparcie

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

Jeśli uważasz to narzędzie za przydatne i chcesz wesprzeć jego rozwój, rozważ postawienie mi kawy!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
