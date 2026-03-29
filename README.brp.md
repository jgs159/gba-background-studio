<p align="center"><img width="1868" height="560" alt="Image" src="https://github.com/user-attachments/assets/a6bc6480-d0bd-4cab-bd0b-72e03e2b4580" /></p>

## GBA Background Studio

**GBA Background Studio** é uma aplicação de desktop para criar e editar **fundos do Game Boy Advance (GBA)**. Permite converter imagens em tilesets e tilemaps compatíveis com GBA, editar tiles e paletas visualmente, e exportar assets prontos para uso em seus projetos GBA.

> ⚠️ Esta aplicação foi desenvolvida para desenvolvedores, ROM hackers e pixel artists que precisam de controle preciso sobre os fundos do GBA.

---

## 🌐 Traduções

Este README está disponível nos seguintes idiomas:

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jap.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Funcionalidades

- **Conversão de imagem para GBA**
  - Converte imagens padrão em tilesets e tilemaps compatíveis com GBA.
  - Configura o tamanho de saída e a profundidade de cor (4bpp e 8bpp).
  - Pré-visualização do resultado antes de exportar.

- **Edição de Tileset**
  - Seleção e edição visual de tiles.
  - Ferramentas de desenho interativas sobre a grade do tilemap.
  - Níveis de zoom de 100% a 800% para edição pixel a pixel.

- **Edição de Paletas**
  - Edite até 256 cores por paleta.
  - Sincronize as alterações de paleta com as pré-visualizações e os tiles.
  - Reordene, substitua ou ajuste cores individuais.

- **Aba de Pré-visualização**
  - Visualize como ficará seu fundo final em uma tela similar à GBA.
  - Valide rapidamente as configurações de tiles e paletas.

- **Histórico de Desfazer / Refazer**
  - Rastreamento completo do histórico de edições.
  - Operações de desfazer e refazer com um amplo buffer de histórico.

- **Interface e barra de status configuráveis**
  - Barra de status detalhada com seleção de tile, coordenadas do tilemap, ID de paleta, estado de espelhamento e nível de zoom.
  - Barra de ferramentas contextual por aba (pré-visualização, tiles, paletas).

- **Suporte a múltiplos idiomas**
  - Sistema de tradução interno (Translator) com seleção de idioma via configuração.
  - Projetado para suportar múltiplos idiomas na interface.

---

## 🖼️ Capturas de Tela

<p align="center"><img width="896" height="590" alt="Image" src="https://github.com/user-attachments/assets/5ccc3bcc-8697-4866-992f-b05f65064b64" /></p>

<p align="center"><img width="876" height="676" alt="Image" src="https://github.com/user-attachments/assets/7704a18b-f108-44f5-9503-facd77cb994e" /></p>

<p align="center"><img width="876" height="676" alt="Image" src="https://github.com/user-attachments/assets/b6c824ba-af9e-49fe-81fc-fd02a9547c25" /></p>

<p align="center"><img width="876" height="676" alt="Image" src="https://github.com/user-attachments/assets/ae341349-1f8a-4ae5-b64f-500356b04204" /></p>

---

## 🏗️ Descrição da Arquitetura

GBA Background Studio é construído com **Python** e **PySide6**, seguindo um design de interface modular:

- **Janela principal (`GBABackgroundStudio`)**
  - Gerencia o estado da aplicação (BPP atual, nível de zoom, seleção de tile e paleta).
  - Hospeda as abas principais e a barra de status personalizada.
  - Carrega e aplica as configurações (incluindo a última sessão de saída).

- **Abas**
  - `PreviewTab` – Pré-visualização do fundo no estilo GBA.
  - `EditTilesTab` – Ferramentas de edição de tiles e tilemap.
  - `EditPalettesTab` – Editor de paletas e ferramentas de manipulação de cores.

- **Componentes e utilitários da interface**
  - `MenuBar` – Operações de arquivo (abrir imagem, exportar arquivos, sair) e ações do editor.
  - `CustomGraphicsView` – `QGraphicsView` estendido com interação baseada em tiles (hover, desenho, seleção, pré-visualização de colagem).
  - `TilemapUtils` – Lógica compartilhada para interação e seleção do tilemap.
  - `HistoryManager` – Gerenciamento de desfazer/refazer para operações do editor.
  - `HoverManager`, `GridManager` – Auxiliares visuais para efeitos de hover e sobreposições de grade.
  - `Translator`, `ConfigManager` – Localização e configuração persistente.

---

## 📦 Instalação

### Requisitos
- **Python** (3.12+ recomendado)
- **Pip** (Gerenciador de pacotes do Python)
- **Sistemas Operacionais compatíveis com PySide6:**
  - **Windows:** Windows 10 (Versão 1809) ou superior.
  - **macOS:** macOS 11 (Big Sur) ou superior.
  - **Linux:** Distribuições modernas com glibc 2.28 ou superior.

### Dependências
As dependências principais incluem:
- `PySide6` (Qt para Python) - *Nota: Requer as versões de SO mencionadas acima.*
- `Pillow` (PIL) para processamento de imagem.

Você pode instalar as dependências usando:
```bash
pip install -r requirements.txt
```

---

### 🏛️ Suporte para Sistemas Legados (Windows 7 / 8 / 8.1)
Se você estiver usando uma versão antiga do Windows que não suporta o **PySide6** (o framework gráfico), ainda poderá usar o motor de conversão através do nosso **Assistente de Linha de Comando Multilíngue**.

Você pode instalar as dependências legadas usando:
```bash
pip install -r requirements-legacy.txt
```

Isso permite converter imagens em assets de GBA sem a interface gráfica, usando um assistente guiado passo a passo em seu idioma nativo.

1. Navegue até a raiz do projeto.
2. Execute o arquivo **`GBA_Studio_Wizard.bat`**.
3. Selecione seu idioma (18 idiomas suportados).
4. Siga as instruções para arrastar sua imagem e configurar a saída para GBA.

---

## 🚀 Primeiros Passos

1. **Clone o repositório**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Crie e ative um ambiente virtual** (opcional, mas recomendado)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # No Windows: .venv\Scripts\activate
   ```

3. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**

   ```bash
   python main.py
   ```

---

## 🧭 Uso Básico

1. **Abrir uma Imagem**
   - Vá em **Arquivo → Abrir Imagem** ou pressione `Ctrl+O`.
   - Selecione a imagem que deseja converter em um fundo GBA.

2. **Configurar a Conversão**
   - Selecione o **Modo de Fundo** (**Modo de Texto** ou **Rotação/Escala**).
   - Escolha a(s) paleta(s) ou Tilemap a usar (apenas para **Modo de Texto 4bpp**).
   - Defina a cor que será usada como transparente.
   - Ajuste o tamanho de saída e outros parâmetros necessários.
   - Clique em **Converter** e a aplicação cuidará do resto.

3. **Editar Tiles**
   - Mude para a aba **Editar Tiles**.
   - Use a visualização do tilemap para desenhar e modificar tiles individuais.
   - Selecione áreas completas para copiar, recortar, colar ou rotacionar grupos de tiles.
   - Sincronize as alterações em tempo real para ver resultados instantâneos.
   - Ajuste o nível de **Zoom** para precisão perfeita.
   - Otimize ou Desotimize tilesets para economizar espaço ou garantir compatibilidade com o hardware.
   - Converta assets entre os formatos **4bpp** e **8bpp**.
   - Alterne entre **Modo de Texto** e **Rotação/Escala** sem problemas.

4. **Editar Paletas**
   - Vá para a aba **Editar Paletas**.
   - Modifique as cores na grade de paletas e ajuste-as com o editor de cores.
   - Selecione áreas específicas ou todos os tiles pertencentes a uma paleta para substituí-los ou trocá-los por outra.

5. **Pré-visualização do Fundo**
   - Mude para a aba **Pré-visualização** para uma representação fiel de como ficará em um GBA real.
   - Verifique se suas configurações de tiles e paletas funcionam perfeitamente juntas.

6. **Exportar Assets**
   - Vá em **Arquivo → Exportar Arquivos** ou pressione `Ctrl+E`.
   - Exporte tilesets, tilemaps e paletas em formatos prontos para integração na sua cadeia de ferramentas de desenvolvimento GBA.
   - Exporte assets individuais separadamente a partir de seus respectivos menus, se necessário.

---

## 🔄 Desfazer / Refazer

A aplicação rastreia suas ações de edição usando um **gerenciador de histórico**:

- **Desfazer** – reverte a última operação.
- **Refazer** – reaplicar uma operação que foi desfeita.

O sistema de histórico mantém um buffer de estados recentes, incluindo edições de tiles, alterações de paleta e operações de tilemap.

---

## ⚙️ Configuração e Localização

### Configuração

A aplicação usa um gerenciador de configuração para armazenar ajustes como:

- Último idioma utilizado
- Último nível de zoom utilizado
- Se deve carregar a última saída ao iniciar
- Outras preferências de interface e editor

As configurações são carregadas ao iniciar e aplicadas à interface e aos menus.

### Localização

Um componente `Translator` gerencia os textos da interface:

- O idioma padrão é configurado através das definições.
- Os arquivos de tradução podem ser adicionados ou editados para suportar mais idiomas.
- Os textos da interface (menus, diálogos, rótulos) passam pelo tradutor.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você quiser ajudar:

1. Faça um fork deste repositório.
2. Crie uma branch de funcionalidade:
   ```bash
   git checkout -b feature/minha-nova-funcionalidade
   ```
3. Confirme suas alterações:
   ```bash
   git commit -am "Adicionar minha nova funcionalidade"
   ```
4. Envie a branch:
   ```bash
   git push origin feature/minha-nova-funcionalidade
   ```
5. Abra um Pull Request descrevendo suas alterações.

Por favor, mantenha seu código consistente com o estilo existente e inclua testes quando possível.

---

## 📄 Licença

Este projeto está licenciado sob a **Licença Pública Geral GNU v3.0 (GPL-3.0)**.  
Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- Obrigado às comunidades de homebrew e ROM hacking do GBA pela documentação e ferramentas.
- Inspirado em editores clássicos de pixel art e utilitários de desenvolvimento para GBA.

---

## 📩 Contato e Suporte

<p align="left">
  <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" />
  <a href="https://discordapp.com/users/213803341988364289">
    <img src="https://img.shields.io/badge/CompuMax-gray?style=for-the-badge" alt="Usuário" />
  </a>
</p>

Se você achar esta ferramenta útil e quiser apoiar seu desenvolvimento, considere me pagar um café!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
