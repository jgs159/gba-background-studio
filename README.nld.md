<p align="center"><img width="1868" height="560" alt="Image" src="https://github.com/user-attachments/assets/a6bc6480-d0bd-4cab-bd0b-72e03e2b4580" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** is een desktopapplicatie voor het maken en bewerken van **Game Boy Advance (GBA)-achtergronden**. Het maakt het mogelijk om afbeeldingen te converteren naar GBA-compatibele tilesets en tilemaps, tegels en paletten visueel te bewerken, en assets te exporteren die klaar zijn voor gebruik in uw GBA-projecten.

> ⚠️ Deze applicatie is ontworpen voor ontwikkelaars, ROM-hackers en pixel-artists die nauwkeurige controle over GBA-achtergronden nodig hebben.

---

## 🌐 Vertalingen

Deze README is beschikbaar in de volgende talen:

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jap.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Functies

- **Afbeelding naar GBA-conversie**
  - Converteert standaardafbeeldingen naar GBA-compatibele tilesets en tilemaps.
  - Configureert uitvoergrootte en kleurdiepte (4bpp en 8bpp).
  - Voorbeeld van het resultaat vóór het exporteren.

- **Tegels Bewerken**
  - Visuele selectie en bewerking van tegels.
  - Interactieve tekenhulpmiddelen op het tilemap-raster.
  - Zoomniveaus van 100% tot 800% voor pixel-voor-pixel bewerking.

- **Paletten Bewerken**
  - Bewerk tot 256 kleuren per palet.
  - Synchroniseer paletwijzigingen met voorbeelden en tegels.
  - Herorden, vervang of pas individuele kleuren aan.

- **Voorbeeld-tabblad**
  - Visualiseer hoe uw uiteindelijke achtergrond eruit zal zien op een GBA-achtig scherm.
  - Valideer snel tegel- en paletconfiguraties.

- **Ongedaan maken/Opnieuw uitvoeren-geschiedenis**
  - Volledige tracking van bewerkingsgeschiedenis.
  - Ongedaan maken en opnieuw uitvoeren met een grote geschiedenisbuffer.

- **Configureerbare interface en statusbalk**
  - Gedetailleerde statusbalk met tegelselectie, tilemap-coördinaten, palet-ID, spiegelstatus en zoomniveau.
  - Contextuele werkbalk per tabblad (voorbeeld, tegels, paletten).

- **Meertalige ondersteuning**
  - Intern vertaalsysteem (Translator) met taalselectie via instellingen.
  - Ontworpen om meerdere talen in de interface te ondersteunen.

---

## 🖼️ Schermafbeeldingen

<p align="center"><img width="896" height="590" alt="Image" src="https://github.com/user-attachments/assets/bcd698df-b3a5-477a-af42-eda13f9c93f6" /></p>

<p align="center"><img width="925" height="676" alt="Image" src="https://github.com/user-attachments/assets/8873256c-3b12-4f15-bf04-401b20ab09dc" /></p>

<p align="center"><img width="925" height="676" alt="Image" src="https://github.com/user-attachments/assets/ae7f129b-2d9f-4fda-be3c-ef5e7da5a0fd" /></p>

<p align="center"><img width="925" height="676" alt="Image" src="https://github.com/user-attachments/assets/f918d167-b7cc-4864-a754-5278fb7e264d" /></p>

---

## 🏗️ Architectuurbeschrijving

GBA Background Studio is gebouwd met **Python** en **PySide6**, en volgt een modulair interfaceontwerp:

- **Hoofdvenster (`GBABackgroundStudio`)**
  - Beheert de applicatiestatus (huidig BPP, zoomniveau, tegel- en paletselectie).
  - Herbergt de hoofdtabbladen en de aangepaste statusbalk.
  - Laadt en past configuratie toe (inclusief de laatste uitvoersessie).

- **Tabbladen**
  - `PreviewTab` – GBA-stijl achtergrondvoorbeeld.
  - `EditTilesTab` – Hulpmiddelen voor tegel- en tilemap-bewerking.
  - `EditPalettesTab` – Paleteditor en kleurmanipulatiehulpmiddelen.

- **Interfacecomponenten en hulpprogramma's**
  - `MenuBar` – Bestandsbewerkingen (afbeelding openen, bestanden exporteren, afsluiten) en editoracties.
  - `CustomGraphicsView` – Uitgebreide `QGraphicsView` met tegelgebaseerde interactie.
  - `TilemapUtils` – Gedeelde logica voor tilemap-interactie en -selectie.
  - `HistoryManager` – Ongedaan maken/opnieuw uitvoeren-beheer voor editorbewerkingen.
  - `HoverManager`, `GridManager` – Visuele hulpmiddelen voor hover-effecten en rasteroverlays.
  - `Translator`, `ConfigManager` – Lokalisatie en persistente configuratie.

---

## 📦 Installatie

### Vereisten
- **Python** (3.12+ aanbevolen)
- **Pip** (Python pakketbeheerder)
- **Besturingssysteem ondersteuning voor PySide6:**
  - **Windows:** Windows 10 (Versie 1809) of nieuwer.
  - **macOS:** macOS 11 (Big Sur) of nieuwer.
  - **Linux:** Moderne distributies met glibc 2.28 of nieuwer.

### Afhankelijkheden
De belangrijkste afhankelijkheden zijn:
- `PySide6` (Qt voor Python) - *Let op: Vereist de hierboven genoemde OS-versies.*
- `Pillow` (PIL) voor beeldbewerking.

U kunt de afhankelijkheden installeren met:
```bash
pip install -r requirements.txt
```

---

### 🏛️ Ondersteuning voor Legacy OS (Windows 7 / 8 / 8.1)
Als u een oudere versie van Windows gebruikt die **PySide6** (het GUI-framework) niet ondersteunt, kunt u nog steeds de conversie-engine gebruiken via onze **Meertalige Command Line Wizard**.

U kunt de legacy-afhankelijkheden installeren met:
```bash
pip install -r requirements-legacy.txt
```

Hiermee kunt u afbeeldingen converteren naar GBA-assets zonder de grafische interface, met behulp van een stapsgewijze assistent in uw eigen taal.

1. Ga naar de hoofdmap van het project.
2. Voer het bestand **`GBA_Studio_Wizard.bat`** uit.
3. Selecteer uw taal (18 talen ondersteund).
4. Volg de instructies om uw afbeelding te slepen en de GBA-output te configureren.

---

## 🚀 Aan de slag

1. **Repository klonen**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Virtuele omgeving aanmaken en activeren** (optioneel maar aanbevolen)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Op Windows: .venv\Scripts\activate
   ```

3. **Afhankelijkheden installeren**

   ```bash
   pip install -r requirements.txt
   ```

4. **Applicatie starten**

   ```bash
   python main.py
   ```

---

## 🧭 Basisgebruik

1. **Een Afbeelding Openen**
   - Ga naar **Bestand → Afbeelding Openen** of druk op `Ctrl+O`.
   - Selecteer de afbeelding die u wilt converteren naar een GBA-achtergrond.

2. **Conversie Configureren**
   - Selecteer de **BG-modus** (**Tekst Modus** of **Rotatie/Schalen**).
   - Kies de palet(ten) of Tilemap om te gebruiken (alleen voor **Tekst Modus 4bpp**).
   - Stel de kleur in die als transparant wordt gebruikt.
   - Pas de uitvoergrootte en andere benodigde parameters aan.
   - Klik op **Converteren** en de applicatie doet de rest.

3. **Tegels Bewerken**
   - Schakel naar het tabblad **Tegels Bewerken**.
   - Gebruik de tilemap-weergave om individuele tegels te tekenen en te wijzigen.
   - Selecteer volledige gebieden om tegelgroepen te kopiëren, knippen, plakken of roteren.
   - Synchroniseer wijzigingen in realtime voor directe resultaten.
   - Pas het **Zoom**-niveau aan voor perfecte precisie.
   - Tegels Optimaliseren/De-optimaliseren om ruimte te besparen of hardwarecompatibiliteit te garanderen.
   - Assets converteren tussen **4bpp** en **8bpp** formaten.
   - Naadloos schakelen tussen **Tekst Modus** en **Rotatie/Schalen**.

4. **Paletten Bewerken**
   - Ga naar het tabblad **Paletten Bewerken**.
   - Wijzig kleuren in het palettenraster en pas ze aan met de kleureneditor.
   - Selecteer specifieke gebieden of alle tegels die tot een palet behoren om ze te vervangen of te wisselen met een ander.

5. **Achtergrondvoorbeeld**
   - Schakel naar het tabblad **Voorbeeld** voor een getrouwe weergave van hoe het eruit zal zien op een echte GBA.
   - Controleer of uw tegel- en paletconfiguraties perfect samenwerken.

6. **Assets Exporteren**
   - Ga naar **Bestand → Bestanden Exporteren** of druk op `Ctrl+E`.
   - Exporteer tilesets, tilemaps en paletten in formaten die klaar zijn voor integratie in uw GBA-ontwikkelingstoolchain.
   - Exporteer individuele assets afzonderlijk vanuit hun respectieve menu's indien nodig.

---

## 🔄 Ongedaan maken/Opnieuw uitvoeren

De applicatie volgt uw bewerkingsacties met een **geschiedenisbeheerder**:

- **Ongedaan maken** – maakt de laatste bewerking ongedaan.
- **Opnieuw uitvoeren** – past een ongedaan gemaakte bewerking opnieuw toe.

Het geschiedenissysteem houdt een buffer bij van recente toestanden, inclusief tegelwijzigingen, paletwijzigingen en tilemap-bewerkingen.

---

## ⚙️ Configuratie en Lokalisatie

### Configuratie

De applicatie gebruikt een configuratiebeheerder om instellingen op te slaan zoals:

- Laatste gebruikte taal
- Laatste gebruikte zoomniveau
- Of de laatste uitvoer bij het opstarten moet worden geladen
- Andere interface- en editorvoorkeuren

De configuratie wordt bij het opstarten geladen en toegepast op de interface en menu's.

### Lokalisatie

Een `Translator`-component beheert de interfaceteksten:

- De standaardtaal wordt geconfigureerd via de instellingen.
- Vertaalbestanden kunnen worden toegevoegd of bewerkt om meer talen te ondersteunen.
- Interfaceteksten (menu's, dialoogvensters, labels) worden door de vertaler verwerkt.

---

## 🤝 Bijdragen

Bijdragen zijn welkom! Als u wilt helpen:

1. Fork dit repository.
2. Maak een feature-branch aan:
   ```bash
   git checkout -b feature/mijn-nieuwe-functie
   ```
3. Bevestig uw wijzigingen:
   ```bash
   git commit -am "Mijn nieuwe functie toevoegen"
   ```
4. Push de branch:
   ```bash
   git push origin feature/mijn-nieuwe-functie
   ```
5. Open een Pull Request met een beschrijving van uw wijzigingen.

Houd uw code consistent met de bestaande stijl en voeg indien mogelijk tests toe.

---

## 📄 Licentie

Dit project is gelicentieerd onder de **GNU General Public License v3.0 (GPL-3.0)**.  
Zie het bestand [LICENSE](LICENSE) voor meer details.

---

## 🙏 Dankbetuigingen

- Dank aan de GBA homebrew- en ROM-hackingcommunity's voor hun documentatie en hulpmiddelen.
- Geïnspireerd door klassieke pixel-art-editors en GBA-ontwikkelingsutiliteiten.

---

## 📩 Contact en Ondersteuning

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

Als u dit hulpmiddel nuttig vindt en de ontwikkeling wilt ondersteunen, overweeg dan om mij een koffie te trakteren!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
