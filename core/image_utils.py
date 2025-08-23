# core/image_utils.py
import os
import numpy as np
from PIL import Image
from shutil import copy2
from PySide6.QtGui import QImage
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from core.config import MARKER_COLOR
from core.palette_utils import rgb_to_gba_rounded
from core.language import translate

def extract_tiles_rgba(img):
    w, h = img.size
    tiles = []
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            box = (x, y, x+8, y+8)
            tile = img.crop(box)
            if tile.size != (8, 8):
                pad = Image.new("P" if img.mode == 'P' else "RGBA", (8, 8), 0)
                pad.paste(tile, (0, 0))
                tile = pad
            tiles.append(tile)
    return tiles

def pil_to_qimage(pil_img):
    """
    Convierte una imagen PIL a QImage para usar en PySide6.
    Soporta modos RGBA y RGB.
    """
    if pil_img.mode == "RGBA":
        data = pil_img.tobytes("raw", "RGBA")
        return QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
    else:
        rgb_img = pil_img.convert("RGB")
        data = rgb_img.tobytes("raw", "RGB")
        return QImage(data, rgb_img.size[0], rgb_img.size[1], QImage.Format_RGB888)
        
def create_gbagfx_preview_4bpp(selected_palettes, transparent_color=(0, 0, 0), keep_transparent=False):
    """
    Genera:
        - temp/preview/preview.png
        - temp/preview/palette.pal
    """
    try:
        output_dir = "output"
        indexed_dir = os.path.join("temp", "02_reindexed")
        preview_dir = os.path.join("temp", "preview")
        os.makedirs(preview_dir, exist_ok=True)

        # === 1. Obtener tamaño desde group_0_indexed.png ===
        base_path = os.path.join(indexed_dir, "group_0_indexed.png")
        if not os.path.exists(base_path):
            print(translate("error_preview_missing", path=base_path))
            return
        sample_img = Image.open(base_path)
        w, h = sample_img.size

        # === 2. Construir full_palette_gba[256] desde output/palette_xx.pal ===
        full_palette_gba = [(0, 0, 0)] * 256

        for base_idx in range(16):
            pal_path = os.path.join(output_dir, f"palette_{base_idx:02d}.pal")
            if not os.path.exists(pal_path):
                continue
            with open(pal_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
            if not lines:
                continue
            try:
                num_colors = int(lines[0])
            except (ValueError, IndexError):
                continue
            for i, line in enumerate(lines[1:1+num_colors]):
                try:
                    r, g, b = map(int, line.split())
                    idx = base_idx * 16 + i
                    if idx < 256:
                        full_palette_gba[idx] = (r, g, b)
                except (ValueError, IndexError):
                    continue

        # Guardar temp/preview/palette.pal
        pal_output = os.path.join(preview_dir, "palette.pal")
        with open(pal_output, "w") as f:
            f.write("JASC-PAL\n0100\n")
            f.write("256\n")
            for r, g, b in full_palette_gba:
                f.write(f"{int(r)} {int(g)} {int(b)}\n")

        # === 3. Crear paleta de 256 colores únicos ===
        unique_colors = []
        for i in range(256):
            r = (i * 57) % 256
            g = (i * 113) % 256
            b = (i * 197) % 256
            unique_colors.append((r, g, b))

        # === 4. Crear imagen base con paleta única ===
        flat_unique = [c for color in unique_colors for c in color] + [0] * (768 - len(unique_colors) * 3)
        result_img = Image.new("P", (w, h), 0)
        result_img.putpalette(flat_unique)

        # === 5. Superponer grupos con paleta única ===
        for i, pal_idx in enumerate(selected_palettes):
            group_path = os.path.join(indexed_dir, f"group_{i}_indexed.png")
            if not os.path.exists(group_path):
                continue

            img = Image.open(group_path)
            if img.mode != 'P':
                continue

            # Obtener la paleta original del grupo para identificar el color transparente
            original_palette = img.getpalette()
            if original_palette:
                # Crear una imagen temporal con la paleta completa de 256 colores
                temp_img = Image.new("P", img.size, 0)
                temp_img.putpalette(flat_unique)
                
                # Convertir a arrays para procesamiento
                img_array = np.array(img)
                temp_array = np.array(temp_img)
                
                # Mapear los índices: los colores del grupo (0-15) se mapean a la paleta única
                # en las posiciones pal_idx*16 a pal_idx*16+15, excepto el transparente
                for original_idx in range(16):
                    target_idx = pal_idx * 16 + original_idx
                    
                    # Solo mapear si no es el color transparente
                    if original_idx != 0:  # El índice 0 es siempre el transparente
                        mask = (img_array == original_idx)
                        temp_array[mask] = target_idx
                
                # Convertir de vuelta a imagen
                img_with_color = Image.fromarray(temp_array, mode="P")
                img_with_color.putpalette(flat_unique)

                # Convertir a array numpy para procesamiento
                result_array = np.array(result_img)
                group_array = np.array(img_with_color)
                
                # Crear máscara: píxeles que NO son transparentes (índice 0 en la imagen original)
                mask = (group_array != 0)
                
                # Aplicar superposición: solo reemplazar donde hay píxeles no transparentes
                result_array[mask] = group_array[mask]
                
                # Convertir de vuelta a imagen
                result_img = Image.fromarray(result_array, mode="P")
                result_img.putpalette(flat_unique)

        # === 6. Aplicar paleta final ===
        flat_gba = [c for color in full_palette_gba for c in color] + [0] * (768 - len(full_palette_gba) * 3)
        
        # Crear una nueva imagen con la paleta final pero manteniendo los índices
        final_img = Image.new("P", (w, h), 0)
        final_img.putpalette(flat_gba)
        
        # Copiar los datos de píxeles (índices) de la imagen compuesta
        final_img.putdata(list(result_img.getdata()))

        # === 7. Guardar preview.png ===
        preview_path = os.path.join(preview_dir, "preview.png")
        final_img.save(preview_path)

    except Exception as e:
        print(translate("error_preview", e=e))

def create_gbagfx_preview_8bpp(transparent_color=None, keep_transparent=False):
    """
    Genera:
        - temp/preview/preview.png (reindexado con paleta ordenada)
        - temp/preview/palette.pal (256 colores, desde output/palette_xxx.pal)
    """
    if transparent_color is None:
        transparent_color = (0, 0, 0)

    try:
        # === 1. Encontrar el archivo de paleta en output/ ===
        output_dir = "output"
        palette_files = [f for f in os.listdir(output_dir) if f.startswith("palette_") and f.endswith(".pal")]
        if not palette_files:
            print(translate("error_preview_no_palette"))
            return

        start_index = None
        pal_path = None
        for f in palette_files:
            stem = f[8:-4]  # "000", "128", etc.
            if stem.isdigit() and len(stem) == 3:
                start_index = int(stem)
                pal_path = os.path.join(output_dir, f)
                break

        if not pal_path or not os.path.exists(pal_path):
            print(translate("error_preview_no_palette"))
            return

        # === 2. Leer paleta desde output/palette_xxx.pal (ya en formato GBA) ===
        with open(pal_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
        if not lines:
            print(translate("error_preview_empty_palette"))
            return

        count = int(lines[0])
        raw_palette = []
        for line in lines[1:1 + count]:
            r, g, b = map(int, line.split())
            raw_palette.append((r, g, b))

        # === 3. Construir paleta completa de 256 colores ===
        # Usar blanco (255,255,255) como marcador para slots no usados
        full_palette = [(255, 255, 255)] * 256  # Inicializar con blanco

        # Índice 0: color transparente
        transparent_color_gba = (int(transparent_color[0]), int(transparent_color[1]), int(transparent_color[2]))
        if keep_transparent:
            full_palette[0] = transparent_color_gba
        else:
            full_palette[0] = (0, 0, 0)

        # Copiar paleta desde start_index
        for i, color in enumerate(raw_palette):
            idx = start_index + i
            if idx < 256:
                full_palette[idx] = color

        # === 4. Cargar y redondear paleta de reconstructed.png ===
        reconstructed_path = "temp/reconstructed.png"
        if not os.path.exists(reconstructed_path):
            print(translate("error_preview_missing", path=reconstructed_path))
            return

        base_img = Image.open(reconstructed_path)
        if base_img.mode != 'P':
            raise ValueError("reconstructed.png must be in indexed mode")

        # Obtener paleta original de reconstructed.png
        orig_pal = base_img.getpalette()
        orig_rgb = []
        for i in range(256):
            if i * 3 + 2 < len(orig_pal):
                r = orig_pal[i * 3]
                g = orig_pal[i * 3 + 1]
                b = orig_pal[i * 3 + 2]
            else:
                r = g = b = 0
            orig_rgb.append((r, g, b))

        # Redondear a GBA para comparación exacta
        orig_gba = [rgb_to_gba_rounded(color) for color in orig_rgb]

        # === 5. Crear mapeo old_index → new_index según full_palette ===
        # Crear diccionario de color a índice, excluyendo slots de relleno blanco
        color_to_index = {}
        for idx, color in enumerate(full_palette):
            if color != (255, 255, 255):  # No incluir slots de relleno
                color_to_index[color] = idx

        index_mapping = {}
        for old_idx, color in enumerate(orig_gba):
            # Buscar coincidencia exacta en full_palette (solo colores reales)
            new_idx = color_to_index.get(color, 0)  # fallback a transparente
            index_mapping[old_idx] = new_idx

        # === 6. Reindexar la imagen ===
        img_array = np.array(base_img)
        new_array = np.zeros_like(img_array)
        for old_idx, new_idx in index_mapping.items():
            new_array[img_array == old_idx] = new_idx
        preview_img = Image.fromarray(new_array, mode="P")

        # Reemplazar todos los blancos de relleno por negro (0,0,0) en la paleta final
        final_palette = []
        for color in full_palette:
            if color == (255, 255, 255):
                final_palette.append((0, 0, 0))  # Reemplazar blanco por negro
            else:
                final_palette.append(color)

        # Aplicar paleta final
        flat_palette = []
        for r, g, b in final_palette:
            flat_palette.extend([int(r), int(g), int(b)])
        while len(flat_palette) < 768:
            flat_palette.append(0)
        preview_img.putpalette(flat_palette)

        # === 7. Guardar preview.png y palette.pal ===
        preview_dir = os.path.join("temp", "preview")
        os.makedirs(preview_dir, exist_ok=True)

        preview_path = os.path.join(preview_dir, "preview.png")
        preview_img.save(preview_path)

        pal_output = os.path.join(preview_dir, "palette.pal")
        with open(pal_output, "w") as f:
            f.write("JASC-PAL\n")
            f.write("0100\n")
            f.write("256\n")
            for r, g, b in final_palette:  # Usar la paleta final con negros
                f.write(f"{int(r)} {int(g)} {int(b)}\n")

    except Exception as e:
        print(translate("error_preview", e=e))
        try:
            copy2("temp/reconstructed.png", os.path.join("temp", "preview", "preview.png"))
        except:
            pass
