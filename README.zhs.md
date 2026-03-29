<p align="center"><img width="1868" height="560" alt="Image" src="https://github.com/user-attachments/assets/a6bc6480-d0bd-4cab-bd0b-72e03e2b4580" /></p>

## GBA Background Studio

**GBA Background Studio** 是一款用于创建和编辑 **Game Boy Advance (GBA) 背景**的桌面应用程序。它允许将图像转换为 GBA 兼容的图块集和图块映射，可视化编辑图块和调色板，并导出可在 GBA 项目中直接使用的资源。

> ⚠️ 此应用程序专为需要精确控制 GBA 背景的开发者、ROM 黑客和像素艺术家设计。

---

## 🌐 翻译

此 README 提供以下语言版本：

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jap.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ 功能特性

- **图像转 GBA**
  - 将标准图像转换为 GBA 兼容的图块集和图块映射。
  - 配置输出尺寸和颜色深度（4bpp 和 8bpp）。
  - 导出前预览结果。

- **编辑图块**
  - 图块的可视化选择和编辑。
  - 图块映射网格上的交互式绘图工具。
  - 100% 至 800% 的缩放级别，支持逐像素编辑。

- **编辑调色板**
  - 每个调色板最多编辑 256 种颜色。
  - 将调色板更改与预览和图块同步。
  - 重新排列、替换或调整单个颜色。

- **预览选项卡**
  - 在类似 GBA 的屏幕上可视化最终背景的外观。
  - 快速验证图块和调色板配置。

- **撤销/重做历史**
  - 完整的编辑历史跟踪。
  - 具有大型历史缓冲区的撤销和重做操作。

- **可配置的界面和状态栏**
  - 详细的状态栏，包含图块选择、图块映射坐标、调色板 ID、翻转状态和缩放级别。
  - 每个选项卡的上下文工具栏（预览、图块、调色板）。

- **多语言支持**
  - 内部翻译系统（Translator），通过设置选择语言。
  - 设计为支持界面中的多种语言。

---

## 🖼️ 截图

<p align="center"><img width="896" height="590" alt="Image" src="https://github.com/user-attachments/assets/37ccf629-95b1-4f7c-961d-7740af21b004" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/4a9542bf-98b7-41b4-909e-1b4160ca9ff8" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/454475ab-ef67-467d-9d5f-e531f12e31b3" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/041cef46-8ee2-487d-b1ce-80b02cabd618" /></p>

---

## 🏗️ 架构说明

GBA Background Studio 使用 **Python** 和 **PySide6** 构建，遵循模块化界面设计：

- **主窗口（`GBABackgroundStudio`）**
  - 管理应用程序状态（当前 BPP、缩放级别、图块和调色板选择）。
  - 承载主选项卡和自定义状态栏。
  - 加载并应用配置（包括最后一次输出会话）。

- **选项卡**
  - `PreviewTab` – GBA 风格的背景预览。
  - `EditTilesTab` – 图块和图块映射编辑工具。
  - `EditPalettesTab` – 调色板编辑器和颜色操作工具。

- **界面组件和实用程序**
  - `MenuBar` – 文件操作（打开图像、导出文件、退出）和编辑器操作。
  - `CustomGraphicsView` – 具有基于图块交互的扩展 `QGraphicsView`。
  - `TilemapUtils` – 图块映射交互和选择的共享逻辑。
  - `HistoryManager` – 编辑器操作的撤销/重做管理。
  - `HoverManager`、`GridManager` – 悬停效果和网格叠加的视觉辅助工具。
  - `Translator`、`ConfigManager` – 本地化和持久配置。

---

## 📦 安装

### 要求
- **Python** (推荐 3.12+)
- **Pip** (Python 包管理器)
- **PySide6 的操作系统支持：**
  - **Windows:** Windows 10 (版本 1809) 或更高版本。
  - **macOS:** macOS 11 (Big Sur) 或更高版本。
  - **Linux:** 带有 glibc 2.28 或更高版本的现代发行版。

### 依赖项
核心依赖项包括：
- `PySide6` (Qt for Python) - *注意：需要上述操作系统版本。*
- `Pillow` (PIL) 用于图像处理。

您可以使用以下命令安装依赖项：
```bash
pip install -r requirements.txt
```

---

### 🏛️ 旧版操作系统支持 (Windows 7 / 8 / 8.1)
如果您使用的旧版本 Windows 不支持 **PySide6**（图形界面框架），您仍然可以通过我们的**多语言命令行向导**使用核心转换引擎。

您可以使用以下命令安装旧版依赖项：
```bash
pip install -r requirements-legacy.txt
```

这允许您在没有图形界面的情况下，使用母语的分步向导将图像转换为 GBA 资源。

1. 导航到项目根目录。
2. 运行 **`GBA_Studio_Wizard.bat`** 文件。
3. 选择您的语言（支持 18 种语言）。
4. 按照说明拖放图像并配置 GBA 输出。

---

## 🚀 快速开始

1. **克隆仓库**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **创建并激活虚拟环境**（可选但推荐）

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # 在 Windows 上：.venv\Scripts\activate
   ```

3. **安装依赖项**

   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用程序**

   ```bash
   python main.py
   ```

---

## 🧭 基本使用

1. **打开图像**
   - 转到**文件 → 打开图像**或按 `Ctrl+O`。
   - 选择要转换为 GBA 背景的图像。

2. **配置转换**
   - 选择**背景模式**（**文本模式**或**旋转/缩放**）。
   - 选择要使用的调色板或图块映射（仅适用于**文本模式 4bpp**）。
   - 设置将用作透明的颜色。
   - 调整输出尺寸和其他必要参数。
   - 点击**转换**，应用程序将处理其余部分。

3. **编辑图块**
   - 切换到**编辑图块**选项卡。
   - 使用图块映射视图绘制和修改单个图块。
   - 选择整个区域以复制、剪切、粘贴或旋转图块组。
   - 实时同步更改以查看即时结果。
   - 调整**缩放**级别以获得完美精度。
   - 优化/取消优化图块以节省空间或确保硬件兼容性。
   - 在 **4bpp** 和 **8bpp** 格式之间转换资源。
   - 在**文本模式**和**旋转/缩放**之间无缝切换。

4. **编辑调色板**
   - 转到**编辑调色板**选项卡。
   - 在调色板网格中修改颜色，并使用颜色编辑器进行调整。
   - 选择特定区域或属于某个调色板的所有图块，以替换或与另一个调色板交换。

5. **背景预览**
   - 切换到**预览**选项卡，以忠实呈现在真实 GBA 上的外观。
   - 验证图块和调色板配置是否完美协同工作。

6. **导出资源**
   - 转到**文件 → 导出文件**或按 `Ctrl+E`。
   - 以可集成到 GBA 开发工具链的格式导出图块集、图块映射和调色板。
   - 如有需要，从各自的菜单单独导出各个资源。

---

## 🔄 撤销/重做

应用程序使用**历史管理器**跟踪您的编辑操作：

- **撤销** – 撤销最后一次操作。
- **重做** – 重新应用已撤销的操作。

历史系统维护最近状态的缓冲区，包括图块编辑、调色板更改和图块映射操作。

---

## ⚙️ 配置和本地化

### 配置

应用程序使用配置管理器存储以下设置：

- 最后使用的语言
- 最后使用的缩放级别
- 启动时是否加载最后的输出
- 其他界面和编辑器偏好设置

配置在启动时加载并应用于界面和菜单。

### 本地化

`Translator` 组件管理界面文本：

- 默认语言通过设置配置。
- 可以添加或编辑翻译文件以支持更多语言。
- 界面文本（菜单、对话框、标签）通过翻译器处理。

---

## 🤝 贡献

欢迎贡献！如果您想提供帮助：

1. Fork 此仓库。
2. 创建功能分支：
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 提交您的更改：
   ```bash
   git commit -am "添加我的新功能"
   ```
4. 推送分支：
   ```bash
   git push origin feature/my-new-feature
   ```
5. 打开描述您更改的 Pull Request。

请保持代码与现有风格一致，并在可能的情况下包含测试。

---

## 📄 许可证

本项目在 **GNU General Public License v3.0 (GPL-3.0)** 下授权。  
有关更多详细信息，请参阅 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 感谢 GBA homebrew 和 ROM 黑客社区提供的文档和工具。
- 受经典像素艺术编辑器和 GBA 开发实用程序的启发。

---

## 📩 联系和支持

<p align="left">
  <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" />
  <a href="https://discordapp.com/users/213803341988364289">
    <img src="https://img.shields.io/badge/CompuMax-gray?style=for-the-badge" alt="用户" />
  </a>
</p>

如果您觉得这个工具有用并想支持其开发，请考虑请我喝杯咖啡！

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
