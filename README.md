---

# GBA Background Studio

**GBA Background Studio** is a desktop application for creating and editing **Game Boy Advance (GBA) backgrounds**. It allows you to convert images into GBA-compatible tilesets and tilemaps, edit tiles and palettes visually, and export ready-to-use assets for your GBA projects.

> ⚠️ This application is designed for developers, ROM hackers, and pixel artists who need fine-grained control over GBA backgrounds.

---

## 🌐 Translations

This README is currently written in English. Translations are available at the following links:

- 🇪🇸 Spanish (es): `README.es.md`
- 🇧🇷 Brazilian Portuguese (pt-BR): `README.brp.md`
- 🇫🇷 French (fr): `README.fr.md`
- 🇩🇪 German (de): `README.deu.md`
- 🇮🇹 Italian (it): `README.ita.md`
- 🇵🇹 European Portuguese (pt-PT): `README.por.md`
- 🇮🇩 Indonesian (id): `README.ind.md`
- 🇮🇳 Hindi (hi): `README.hin.md`
- 🇷🇺 Russian (ru): `README.rus.md`
- 🇯🇵 Japanese (ja): `README.jpn.md`
- 🇨🇳 Simplified Chinese (zh-Hans): `README.zhs.md`
- 🇹🇼 Traditional Chinese (zh-Hant): `README.zht.md`
- 🇰🇷 Korean (ko): `README.kor.md`
- 🇵🇱 Polish (pl): `README.pol.md`
- 🇳🇱 Dutch (nl): `README.nld.md`
- 🇹🇷 Turkish (tr): `README.tur.md`
- 🇻🇳 Vietnamese (vi): `README.vie.md`

---

## ✨ Features

- **Image to GBA conversion**
  - Convert standard images into GBA-friendly tilesets and tilemaps.
  - Configure output size and color depth (4bpp and 8bpp).
  - Preview the result before exporting.

- **Tileset editing**
  - Visual tile selection and editing.
  - Interactive drawing tools on the tilemap grid.
  - Zoom levels from \(100\%\) to \(800\%\) for pixel-perfect editing.

- **Palette editing**
  - Edit up to 256 colors per palette.
  - Synchronize palette changes with previews and tiles.
  - Reorder, replace, or tweak individual colors.

- **Preview tab**
  - See how your final background will look on a GBA-like screen.
  - Quickly validate tile and palette configurations.

- **Undo / Redo history**
  - Comprehensive history tracking for edits.
  - Undo and redo operations with a large history buffer.

- **Configurable UI & status bar**
  - Detailed status bar with tile selection, tilemap coordinates, palette ID, flip state, and zoom level.
  - Context-sensitive toolbar per tab (preview, tiles, palettes).

- **Multi-language support**
  - Internal translation system (Translator) with language selection via configuration.
  - Designed to support multiple languages in the UI.

---

## 🖼️ Screenshots

> <!-- TODO: Insert main window screenshot here (overall app layout, showing tabs and preview).  
> Example:  
> ![Main window of GBA Background Studio showing the preview, tile editor, and palette editor tabs.](path/to/main_window_screenshot.png) -->

> <!-- TODO: Insert conversion dialog screenshot here (input image and GBA output preview).  
> Example:  
> ![Conversion dialog displaying the source image on the left and the GBA-formatted preview on the right, with configuration options.](path/to/conversion_dialog_screenshot.png) -->

> <!-- TODO: Insert palette editor screenshot here (palette grid and color editor).  
> Example:  
> ![Palette editor tab showing the color grid, selection overlays, and color sliders for fine-tuning.](path/to/palette_editor_screenshot.png) -->

---

## 🏗️ Architecture Overview

GBA Background Studio is built with **Python** and **PySide6**, and follows a modular UI design:

- **Main window (`GBABackgroundStudio`)**
  - Manages application state (current BPP, zoom level, tile and palette selection).
  - Hosts the main tabs and the custom status bar.
  - Loads and applies configuration (including last session output).

- **Tabs**
  - `PreviewTab` – GBA-style preview of the background.
  - `EditTilesTab` – Tile and tilemap editing tools.
  - `EditPalettesTab` – Palette editor and color manipulation tools.

- **UI components & utilities**
  - `MenuBar` – File operations (open image, export files, exit) and editor actions.
  - `CustomGraphicsView` – Extended `QGraphicsView` with tile-based interaction (hover, drawing, selection, paste preview).
  - `TilemapUtils` – Shared logic for tilemap interaction and selection.
  - `HistoryManager` – Undo/redo management for editor operations.
  - `HoverManager`, `GridManager` – Visual helpers for hover effects and grid overlays.
  - `Translator`, `ConfigManager` – Localization and persistent configuration.

This separation makes it easier to maintain and extend the application.

---

## 📦 Installation

### Requirements

- **Python** \(3.12+ recommended\)
- **Pip** (Python package manager)
- A supported desktop environment (Windows, macOS, or Linux)

### Dependencies

Core dependencies include:

- `PySide6` (Qt for Python)
- `Pillow` (PIL) for image processing

You can install dependencies using:

```bash
pip install -r requirements.txt
```

---

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/jgs159/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Create and activate a virtual environment** (optional but recommended)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

---

## 🧭 Basic Usage

1. **Open an image**
   - Use **File → Open Image** or press **Ctrl+O**.
   - Select the image you want to convert to a GBA background.

2. **Configure conversion**
   - Adjust output size and color depth (\(4\text{bpp}\) or \(8\text{bpp}\)).
   - Use the conversion dialog to see a preview of the GBA-formatted result.

3. **Edit tiles**
   - Switch to the **Edit Tiles** tab.
   - Use the tilemap view to draw and modify tiles.
   - Zoom in/out to work at the desired scale.

4. **Edit palettes**
   - Go to the **Edit Palettes** tab.
   - Edit colors in the palette grid and tweak them via the color editor.
   - Sync palettes with the preview and tiles as needed.

5. **Preview the background**
   - Switch to the **Preview** tab to see a GBA-like preview.
   - Verify that tiles and palettes look correct together.

6. **Export files**
   - Use **File → Export Files** or press **Ctrl+E**.
   - Export tilesets, tilemaps, and palettes in formats ready to be integrated into your GBA toolchain.

---

## 🔄 Undo / Redo

The application tracks your editing actions using a **history manager**:

- **Undo** – revert the last operation.
- **Redo** – re-apply an operation that was undone.

The history system keeps a buffer of recent states, including tile edits, palette changes, and tilemap operations.

---

## ⚙️ Configuration & Localization

### Configuration

The app uses a configuration manager to store settings such as:

- Last used language
- Last used zoom level
- Whether to load the last output on startup
- Other UI and editor preferences

The configuration is loaded on startup and applied to the UI and menus.

### Localization

A `Translator` component handles the UI text:

- Default language is configured through the settings.
- Translation files can be added or edited to support more languages.
- UI texts (menus, dialogs, labels) are passed through the translator.

---

## 🧪 Testing

> Describe how to run tests if you have any. For example:

```bash
pytest
```

or

```bash
python -m unittest
```

If you don’t have tests yet, you can either omit this section or add a short note stating that tests are planned.

---

## 🤝 Contributing

Contributions are welcome! If you’d like to help:

1. Fork this repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. Commit your changes:
   ```bash
   git commit -am "Add my new feature"
   ```
4. Push the branch:
   ```bash
   git push origin feature/my-new-feature
   ```
5. Open a Pull Request describing your changes.

Please keep your code consistent with the existing style and include tests when possible.

---

## 📄 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for more details.

---

## 🙏 Acknowledgments

- Thanks to the GBA homebrew and ROM hacking communities for their documentation and tools.
- Inspired by classic pixel art editors and GBA development utilities.

---