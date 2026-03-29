<p align="center"><img width="1868" height="560" alt="Image" src="https://github.com/user-attachments/assets/a6bc6480-d0bd-4cab-bd0b-72e03e2b4580" /></p>

## GBA Background Studio

**GBA Background Studio** es una aplicación de escritorio para crear y editar **fondos de Game Boy Advance (GBA)**. Permite convertir imágenes en tilesets y tilemaps compatibles con GBA, editar tiles y paletas visualmente, y exportar assets listos para usar en tus proyectos GBA.

> ⚠️ Esta aplicación está diseñada para desarrolladores, ROM hackers y pixel artists que necesitan control preciso sobre los fondos de GBA.

---

## 🌐 Traducciones

Este README está disponible en los siguientes idiomas:

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jap.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Características

- **Conversión de imagen a GBA**
  - Convierte imágenes estándar en tilesets y tilemaps compatibles con GBA.
  - Configura el tamaño de salida y la profundidad de color (4bpp y 8bpp).
  - Vista previa del resultado antes de exportar.

- **Edición de Tileset**
  - Selección y edición visual de tiles.
  - Herramientas de dibujo interactivas sobre la cuadrícula del tilemap.
  - Niveles de zoom del 100% al 800% para edición pixel a pixel.

- **Edición de Paletas**
  - Edita hasta 256 colores por paleta.
  - Sincroniza los cambios de paleta con las vistas previas y los tiles.
  - Reordena, reemplaza o ajusta colores individuales.

- **Pestaña de Vista Previa**
  - Visualiza cómo quedará tu fondo final en una pantalla similar a la GBA.
  - Valida rápidamente las configuraciones de tiles y paletas.

- **Historial de Deshacer / Rehacer**
  - Seguimiento completo del historial de ediciones.
  - Operaciones de deshacer y rehacer con un amplio buffer de historial.

- **Interfaz y barra de estado configurables**
  - Barra de estado detallada con selección de tile, coordenadas del tilemap, ID de paleta, estado de volteo y nivel de zoom.
  - Barra de herramientas contextual por pestaña (vista previa, tiles, paletas).

- **Soporte multiidioma**
  - Sistema de traducción interno (Translator) con selección de idioma mediante configuración.
  - Diseñado para soportar múltiples idiomas en la interfaz.

---

## 🖼️ Capturas de Pantalla

<p align="center"><img width="896" height="590" alt="Image" src="https://github.com/user-attachments/assets/e707de2f-e314-4662-9cf6-164ee48c33e0" /></p>

<p align="center"><img width="854" height="676" alt="Image" src="https://github.com/user-attachments/assets/c588c56d-0e98-4214-8b9d-50bd2ad0c992" /></p>

<p align="center"><img width="854" height="676" alt="Image" src="https://github.com/user-attachments/assets/d4a9ece2-fe8a-4bd4-9f74-f46e123c541f" /></p>

<p align="center"><img width="854" height="676" alt="Image" src="https://github.com/user-attachments/assets/baf1cff0-4eef-4f2c-a99c-8dfaa214f8c2" /></p>

---

## 🏗️ Descripción de la Arquitectura

GBA Background Studio está construido con **Python** y **PySide6**, y sigue un diseño de interfaz modular:

- **Ventana principal (`GBABackgroundStudio`)**
  - Gestiona el estado de la aplicación (BPP actual, nivel de zoom, selección de tile y paleta).
  - Aloja las pestañas principales y la barra de estado personalizada.
  - Carga y aplica la configuración (incluyendo la última sesión de salida).

- **Pestañas**
  - `PreviewTab` – Vista previa del fondo al estilo GBA.
  - `EditTilesTab` – Herramientas de edición de tiles y tilemap.
  - `EditPalettesTab` – Editor de paletas y herramientas de manipulación de colores.

- **Componentes y utilidades de la interfaz**
  - `MenuBar` – Operaciones de archivo (abrir imagen, exportar archivos, salir) y acciones del editor.
  - `CustomGraphicsView` – `QGraphicsView` extendido con interacción basada en tiles (hover, dibujo, selección, vista previa de pegado).
  - `TilemapUtils` – Lógica compartida para la interacción y selección del tilemap.
  - `HistoryManager` – Gestión de deshacer/rehacer para operaciones del editor.
  - `HoverManager`, `GridManager` – Ayudas visuales para efectos de hover y superposiciones de cuadrícula.
  - `Translator`, `ConfigManager` – Localización y configuración persistente.

---

## 📦 Instalación

### Requisitos
- **Python** (3.12+ recomendado)
- **Pip** (Gestor de paquetes de Python)
- **Sistemas Operativos compatibles con PySide6:**
  - **Windows:** Windows 10 (Versión 1809) o posterior.
  - **macOS:** macOS 11 (Big Sur) o posterior.
  - **Linux:** Distribuciones modernas con glibc 2.28 o posterior (ej. Ubuntu 20.04+, Debian 11+).

### Dependencias
Las dependencias principales incluyen:
- `PySide6` (Qt para Python) - *Nota: Requiere las versiones de SO mencionadas arriba.*
- `Pillow` (PIL) para el procesamiento de imágenes.

Puedes instalar las dependencias usando:
```bash
pip install -r requirements.txt
```

---

### 🏛️ Soporte para Sistemas Legacy (Windows 7 / 8 / 8.1)
Si utilizas una versión antigua de Windows que no soporta **PySide6** (el entorno gráfico), aún puedes usar el motor de conversión a través de nuestro **Asistente de Línea de Comandos Multilingüe**.

Puedes instalar las dependencias legacy usando:
```bash
pip install -r requirements-legacy.txt
```

Esto te permite convertir imágenes en assets de GBA sin la interfaz gráfica, mediante un asistente guiado paso a paso en tu idioma nativo.

1. Dirígete a la raíz del proyecto.
2. Ejecuta el archivo **`GBA_Studio_Wizard.bat`**.
3. Selecciona tu idioma (18 idiomas soportados).
4. Sigue las instrucciones para arrastrar tu imagen y configurar la salida para GBA.

---

## 🚀 Primeros Pasos

1. **Clona el repositorio**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Crea y activa un entorno virtual** (opcional pero recomendado)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # En Windows: .venv\Scripts\activate
   ```

3. **Instala las dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación**

   ```bash
   python main.py
   ```

---

## 🧭 Uso Básico

1. **Abrir una Imagen**
   - Ve a **Archivo → Abrir imagen** o presiona `Ctrl+O`.
   - Selecciona la imagen que deseas convertir en un fondo GBA.

2. **Configurar la Conversión**
   - Selecciona el **Modo de Fondo** (**Modo Texto** o **Modo Rotación/Escalado**).
   - Elige la(s) paleta(s) o Tilemap a usar (solo para **Modo Texto 4bpp**).
   - Establece el color que se usará como transparente.
   - Ajusta el tamaño de salida y otros parámetros necesarios.
   - Haz clic en **Convertir** y la aplicación se encargará del resto.

3. **Editar Tiles**
   - Cambia a la pestaña **Editar Tiles**.
   - Usa la vista del tilemap para dibujar y modificar tiles individuales.
   - Selecciona áreas completas para copiar, cortar, pegar o rotar grupos de tiles.
   - Sincroniza los cambios en tiempo real para ver resultados instantáneos.
   - Ajusta el nivel de **Zoom** para una precisión perfecta.
   - Optimiza o Desoptimiza tilesets para ahorrar espacio o garantizar compatibilidad con el hardware.
   - Convierte assets entre los formatos **4bpp** y **8bpp**.
   - Cambia entre **Modo Texto** y **Modo Rotación/Escalado** sin problemas.

4. **Editar Paletas**
   - Ve a la pestaña **Editar Paletas**.
   - Modifica los colores en la cuadrícula de paletas y ajústalos con el editor de colores.
   - Selecciona áreas específicas o todos los tiles pertenecientes a una paleta para reemplazarlos o intercambiarlos con otra.

5. **Vista Previa del Fondo**
   - Cambia a la pestaña **Vista Previa** para una representación fiel de cómo se verá en una GBA real.
   - Verifica que tus configuraciones de tiles y paletas funcionen perfectamente juntas.

6. **Exportar Assets**
   - Ve a **Archivo → Exportar archivos** o presiona `Ctrl+E`.
   - Exporta tilesets, tilemaps y paletas en formatos listos para ser integrados en tu cadena de herramientas de desarrollo GBA.
   - Exporta assets individuales por separado desde sus respectivos menús si es necesario.

---

## 🔄 Deshacer / Rehacer

La aplicación rastrea tus acciones de edición usando un **gestor de historial**:

- **Deshacer** – revierte la última operación.
- **Rehacer** – vuelve a aplicar una operación que fue deshecha.

El sistema de historial mantiene un buffer de estados recientes, incluyendo ediciones de tiles, cambios de paleta y operaciones de tilemap.

---

## ⚙️ Configuración y Localización

### Configuración

La aplicación usa un gestor de configuración para almacenar ajustes como:

- Último idioma utilizado
- Último nivel de zoom utilizado
- Si cargar la última salida al iniciar
- Otras preferencias de interfaz y editor

La configuración se carga al iniciar y se aplica a la interfaz y los menús.

### Localización

Un componente `Translator` gestiona los textos de la interfaz:

- El idioma predeterminado se configura a través de los ajustes.
- Los archivos de traducción pueden añadirse o editarse para soportar más idiomas.
- Los textos de la interfaz (menús, diálogos, etiquetas) pasan por el traductor.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si deseas ayudar:

1. Haz un fork de este repositorio.
2. Crea una rama de características:
   ```bash
   git checkout -b feature/mi-nueva-caracteristica
   ```
3. Confirma tus cambios:
   ```bash
   git commit -am "Añadir mi nueva característica"
   ```
4. Sube la rama:
   ```bash
   git push origin feature/mi-nueva-caracteristica
   ```
5. Abre un Pull Request describiendo tus cambios.

Por favor, mantén tu código consistente con el estilo existente e incluye pruebas cuando sea posible.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia Pública General GNU v3.0 (GPL-3.0)**.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- Gracias a las comunidades de homebrew y ROM hacking de GBA por su documentación y herramientas.
- Inspirado en editores clásicos de pixel art y utilidades de desarrollo para GBA.

---

## 📩 Contacto y Soporte

<p align="left">
  <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" />
  <a href="https://discordapp.com/users/213803341988364289">
    <img src="https://img.shields.io/badge/CompuMax-gray?style=for-the-badge" alt="Usuario" />
  </a>
</p>

Si encuentras esta herramienta útil y deseas apoyar su desarrollo, ¡considera invitarme un café!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
