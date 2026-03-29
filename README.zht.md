<p align="center"><img width="1868" height="560" alt="Image" src="https://github.com/user-attachments/assets/a6bc6480-d0bd-4cab-bd0b-72e03e2b4580" /></p>

## GBA Background Studio

**GBA Background Studio** 是一款用於建立和編輯 **Game Boy Advance (GBA) 背景**的桌面應用程式。它允許將圖像轉換為 GBA 相容的圖塊集和圖塊映射，可視化編輯圖塊和調色盤，並匯出可在 GBA 專案中直接使用的資源。

> ⚠️ 此應用程式專為需要精確控制 GBA 背景的開發者、ROM 駭客和像素藝術家設計。

---

## 🌐 翻譯

此 README 提供以下語言版本：

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jap.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ 功能特性

- **圖像轉 GBA**
  - 將標準圖像轉換為 GBA 相容的圖塊集和圖塊映射。
  - 設定輸出尺寸和顏色深度（4bpp 和 8bpp）。
  - 匯出前預覽結果。

- **編輯圖塊**
  - 圖塊的可視化選擇和編輯。
  - 圖塊映射網格上的互動式繪圖工具。
  - 100% 至 800% 的縮放級別，支援逐像素編輯。

- **編輯調色盤**
  - 每個調色盤最多編輯 256 種顏色。
  - 將調色盤更改與預覽和圖塊同步。
  - 重新排列、替換或調整個別顏色。

- **預覽分頁**
  - 在類似 GBA 的螢幕上可視化最終背景的外觀。
  - 快速驗證圖塊和調色盤設定。

- **復原/重做歷史**
  - 完整的編輯歷史追蹤。
  - 具有大型歷史緩衝區的復原和重做操作。

- **可設定的介面和狀態列**
  - 詳細的狀態列，包含圖塊選擇、圖塊映射座標、調色盤 ID、翻轉狀態和縮放級別。
  - 每個分頁的上下文工具列（預覽、圖塊、調色盤）。

- **多語言支援**
  - 內部翻譯系統（Translator），透過設定選擇語言。
  - 設計為支援介面中的多種語言。

---

## 🖼️ 截圖

<p align="center"><img width="896" height="590" alt="Image" src="https://github.com/user-attachments/assets/ef22c454-7f0b-4dc0-a48e-76dd4e95aae5" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/a66d42bf-70a2-4d29-9306-dfc4385ce509" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/9bd8bb74-6e99-4e6b-a7c5-27c4d57fa72d" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/bdb5f593-fbb5-4496-a1dc-49ed5a947553" /></p>

---

## 🏗️ 架構說明

GBA Background Studio 使用 **Python** 和 **PySide6** 建構，遵循模組化介面設計：

- **主視窗（`GBABackgroundStudio`）**
  - 管理應用程式狀態（目前 BPP、縮放級別、圖塊和調色盤選擇）。
  - 承載主分頁和自訂狀態列。
  - 載入並套用設定（包括最後一次輸出工作階段）。

- **分頁**
  - `PreviewTab` – GBA 風格的背景預覽。
  - `EditTilesTab` – 圖塊和圖塊映射編輯工具。
  - `EditPalettesTab` – 調色盤編輯器和顏色操作工具。

- **介面元件和公用程式**
  - `MenuBar` – 檔案操作（開啟圖像、匯出檔案、結束）和編輯器操作。
  - `CustomGraphicsView` – 具有基於圖塊互動的擴充 `QGraphicsView`。
  - `TilemapUtils` – 圖塊映射互動和選擇的共用邏輯。
  - `HistoryManager` – 編輯器操作的復原/重做管理。
  - `HoverManager`、`GridManager` – 懸停效果和網格疊加的視覺輔助工具。
  - `Translator`、`ConfigManager` – 本地化和持久設定。

---

## 📦 安裝

### 要求
- **Python** (推薦 3.12+)
- **Pip** (Python 套件管理器)
- **PySide6 的作業系統支援：**
  - **Windows:** Windows 10 (版本 1809) 或更高版本。
  - **macOS:** macOS 11 (Big Sur) 或更高版本。
  - **Linux:** 帶有 glibc 2.28 或更高版本的現代發行版。

### 依賴項
核心依賴項包括：
- `PySide6` (Qt for Python) - *注意：需要上述作業系統版本。*
- `Pillow` (PIL) 用於圖像處理。

您可以使用以下命令安裝依賴項：
```bash
pip install -r requirements.txt
```

---

### 🏛️ 舊版作業系統支援 (Windows 7 / 8 / 8.1)
如果您使用的舊版本 Windows 不支援 **PySide6**（圖形介面框架），您仍然可以透過我們的**多語言命令行精靈**使用核心轉換引擎。

您可以使用以下命令安裝舊版依賴項：
```bash
pip install -r requirements-legacy.txt
```

這允許您在沒有圖形界面的情況下，使用母語的分步精靈將圖像轉換為 GBA 資源。

1. 導航到專案根目錄。
2. 執行 **`GBA_Studio_Wizard.bat`** 檔案。
3. 選擇您的語言（支援 18 種語言）。
4. 按照說明拖放圖像並設定 GBA 輸出。

---

## 🚀 快速開始

1. **複製儲存庫**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **建立並啟用虛擬環境**（可選但建議）

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # 在 Windows 上：.venv\Scripts\activate
   ```

3. **安裝相依性**

   ```bash
   pip install -r requirements.txt
   ```

4. **執行應用程式**

   ```bash
   python main.py
   ```

---

## 🧭 基本使用

1. **開啟圖像**
   - 前往**檔案 → 開啟圖像**或按 `Ctrl+O`。
   - 選擇要轉換為 GBA 背景的圖像。

2. **設定轉換**
   - 選擇**背景模式**（**文字模式**或**旋轉/縮放**）。
   - 選擇要使用的調色盤或圖塊映射（僅適用於**文字模式 4bpp**）。
   - 設定將用作透明的顏色。
   - 調整輸出尺寸和其他必要參數。
   - 點擊**轉換**，應用程式將處理其餘部分。

3. **編輯圖塊**
   - 切換到**編輯圖塊**分頁。
   - 使用圖塊映射檢視繪製和修改個別圖塊。
   - 選擇整個區域以複製、剪下、貼上或旋轉圖塊群組。
   - 即時同步更改以查看即時結果。
   - 調整**縮放**級別以獲得完美精度。
   - 優化/取消優化圖塊以節省空間或確保硬體相容性。
   - 在 **4bpp** 和 **8bpp** 格式之間轉換資源。
   - 在**文字模式**和**旋轉/縮放**之間無縫切換。

4. **編輯調色盤**
   - 前往**編輯調色盤**分頁。
   - 在調色盤網格中修改顏色，並使用顏色編輯器進行調整。
   - 選擇特定區域或屬於某個調色盤的所有圖塊，以替換或與另一個調色盤交換。

5. **背景預覽**
   - 切換到**預覽**分頁，以忠實呈現在真實 GBA 上的外觀。
   - 驗證圖塊和調色盤設定是否完美協同運作。

6. **匯出資源**
   - 前往**檔案 → 匯出檔案**或按 `Ctrl+E`。
   - 以可整合到 GBA 開發工具鏈的格式匯出圖塊集、圖塊映射和調色盤。
   - 如有需要，從各自的選單單獨匯出各個資源。

---

## 🔄 復原/重做

應用程式使用**歷史管理員**追蹤您的編輯操作：

- **復原** – 復原最後一次操作。
- **重做** – 重新套用已復原的操作。

歷史系統維護最近狀態的緩衝區，包括圖塊編輯、調色盤更改和圖塊映射操作。

---

## ⚙️ 設定和本地化

### 設定

應用程式使用設定管理員儲存以下設定：

- 最後使用的語言
- 最後使用的縮放級別
- 啟動時是否載入最後的輸出
- 其他介面和編輯器偏好設定

設定在啟動時載入並套用於介面和選單。

### 本地化

`Translator` 元件管理介面文字：

- 預設語言透過設定設定。
- 可以新增或編輯翻譯檔案以支援更多語言。
- 介面文字（選單、對話框、標籤）透過翻譯器處理。

---

## 🤝 貢獻

歡迎貢獻！如果您想提供協助：

1. Fork 此儲存庫。
2. 建立功能分支：
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 提交您的更改：
   ```bash
   git commit -am "新增我的新功能"
   ```
4. 推送分支：
   ```bash
   git push origin feature/my-new-feature
   ```
5. 開啟描述您更改的 Pull Request。

請保持程式碼與現有風格一致，並在可能的情況下包含測試。

---

## 📄 授權

本專案在 **GNU General Public License v3.0 (GPL-3.0)** 下授權。  
有關更多詳細資訊，請參閱 [LICENSE](LICENSE) 檔案。

---

## 🙏 致謝

- 感謝 GBA homebrew 和 ROM 駭客社群提供的文件和工具。
- 受經典像素藝術編輯器和 GBA 開發公用程式的啟發。

---

## 📩 聯絡和支援

<p align="left">
  <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" />
  <a href="https://discordapp.com/users/213803341988364289">
    <img src="https://img.shields.io/badge/CompuMax-gray?style=for-the-badge" alt="使用者" />
  </a>
</p>

如果您覺得這個工具有用並想支援其開發，請考慮請我喝杯咖啡！

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
