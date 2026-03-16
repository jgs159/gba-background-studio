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
from utils.translator import Translator
translator = Translator()

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
    Converts a PIL image to QImage for use in PySide6.
    Supports RGBA and RGB modes.
    """
    if pil_img.mode == "RGBA":
        data = pil_img.tobytes("raw", "RGBA")
        return QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
    else:
        rgb_img = pil_img.convert("RGB")
        data = rgb_img.tobytes("raw", "RGB")
        return QImage(data, rgb_img.size[0], rgb_img.size[1], QImage.Format_RGB888)

def create_gbagfx_preview_4bpp(save_preview=False, selected_palettes=None, transparent_color=(0, 0, 0), keep_transparent=False, tilemap_width=32, tilemap_height=32):
    """
    Genera:
        - temp/preview/preview.png
        - temp/preview/palette.pal
    """
    try:
        from shutil import copy2
        import numpy as np
        import os
        from PIL import Image

        output_dir = "output"
        preview_dir = os.path.join("temp", "preview")
        os.makedirs(preview_dir, exist_ok=True)

        tiles_path = os.path.join(output_dir, "tiles.png")
        map_path = os.path.join(output_dir, "map.bin")

        if not os.path.exists(tiles_path) or not os.path.exists(map_path):
            print(translator.tr("error_preview_missing_files"))
            return

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
                        if i == 0 and not keep_transparent:
                            full_palette_gba[idx] = (0, 0, 0)
                        else:
                            full_palette_gba[idx] = (r, g, b)
                except (ValueError, IndexError):
                    continue

        pal_output = os.path.join(preview_dir, "palette.pal")
        with open(pal_output, "w") as f:
            f.write("JASC-PAL\n0100\n")
            f.write("256\n")
            for r, g, b in full_palette_gba:
                f.write(f"{int(r)} {int(g)} {int(b)}\n")

        with Image.open(tiles_path) as ts_img:
            tileset_data = np.array(ts_img)
            ts_width, ts_height = ts_img.size

        with open(map_path, "rb") as f:
            map_bytes = f.read()
        
        num_entries = len(map_bytes) // 2
        
        stride_tiles = tilemap_width
        rows_tiles = tilemap_height
        
        preview_array = np.zeros((rows_tiles * 8, stride_tiles * 8), dtype=np.uint8)

        for i in range(min(num_entries, stride_tiles * rows_tiles)):
            entry = int.from_bytes(map_bytes[i*2:i*2+2], "little")
            tile_idx = entry & 0x03FF
            h_flip = (entry >> 10) & 1
            v_flip = (entry >> 11) & 1
            pal_slot = (entry >> 12) & 0xF
            
            tx = (tile_idx % (ts_width // 8)) * 8
            ty = (tile_idx // (ts_width // 8)) * 8
            
            tile_data = tileset_data[ty:ty+8, tx:tx+8].copy()
            if h_flip: 
                tile_data = np.fliplr(tile_data)
            if v_flip: 
                tile_data = np.flipud(tile_data)
            
            px = (i % stride_tiles) * 8
            py = (i // stride_tiles) * 8
            preview_array[py:py+8, px:px+8] = (tile_data % 16) + (pal_slot * 16)

        final_preview = Image.fromarray(preview_array, mode="P")
        
        flat_palette = []
        for r, g, b in full_palette_gba:
            flat_palette.extend([r, g, b])
        
        final_preview.putpalette(flat_palette)
        preview_path = os.path.join(preview_dir, "preview.png")
        final_preview.save(preview_path)

        if save_preview:
            os.makedirs("output", exist_ok=True)
            copy2(preview_path, os.path.join("output", "preview_image.png"))
            copy2(pal_output, os.path.join("output", "preview_palette.pal"))

        print(translator.tr("preview_generated"))

    except Exception as e:
        print(translator.tr("error_preview", e=e))

def create_gbagfx_preview_8bpp(save_preview=False, transparent_color=None, keep_transparent=False, quantized_img=None, tilemap_width=32, tilemap_height=32):
    if transparent_color is None:
        transparent_color = (0, 0, 0)

    try:
        output_dir = "output"
        palette_files = [f for f in os.listdir(output_dir) if f.startswith("palette_") and f.endswith(".pal")]
        if not palette_files:
            print(translator.tr("error_preview_no_palette"))
            return

        start_index = None
        pal_path = None
        for f in palette_files:
            stem = f[8:-4]
            if stem.isdigit() and len(stem) == 3:
                start_index = int(stem)
                pal_path = os.path.join(output_dir, f)
                break

        if not pal_path or not os.path.exists(pal_path):
            print(translator.tr("error_preview_no_palette"))
            return

        with open(pal_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
        if not lines:
            print(translator.tr("error_preview_empty_palette"))
            return

        count = int(lines[0])
        raw_palette = []
        for line in lines[1:1 + count]:
            r, g, b = map(int, line.split())
            raw_palette.append((r, g, b))

        full_palette = [(0, 0, 0)] * 256
        if keep_transparent:
            full_palette[0] = (int(transparent_color[0]), int(transparent_color[1]), int(transparent_color[2]))

        for i, color in enumerate(raw_palette):
            idx = start_index + i
            if idx < 256:
                full_palette[idx] = color

        # Usar quantized_img en memoria si está disponible, si no leer del disco
        if quantized_img is not None:
            base_img = quantized_img
        else:
            reconstructed_path = os.path.join("temp", "reconstructed.png")
            if not os.path.exists(reconstructed_path):
                print(translator.tr("error_preview_missing", path=reconstructed_path))
                return
            base_img = Image.open(reconstructed_path)

        if base_img.mode != 'P':
            raise ValueError("Image must be in indexed mode")

        orig_pal = base_img.getpalette()
        orig_rgb = []
        for i in range(256):
            if i * 3 + 2 < len(orig_pal):
                r, g, b = orig_pal[i*3], orig_pal[i*3+1], orig_pal[i*3+2]
            else:
                r = g = b = 0
            orig_rgb.append((r, g, b))

        orig_gba = [rgb_to_gba_rounded(color) for color in orig_rgb]

        color_to_index = {color: idx for idx, color in enumerate(full_palette) if color != (0, 0, 0)}

        index_mapping = {old_idx: color_to_index.get(color, 0) for old_idx, color in enumerate(orig_gba)}

        img_array = np.array(base_img)
        new_array = np.zeros_like(img_array)
        for old_idx, new_idx in index_mapping.items():
            new_array[img_array == old_idx] = new_idx
        preview_img = Image.fromarray(new_array, mode="P")

        flat_palette = []
        for r, g, b in full_palette:
            flat_palette.extend([int(r), int(g), int(b)])
        while len(flat_palette) < 768:
            flat_palette.append(0)
        preview_img.putpalette(flat_palette)

        preview_dir = os.path.join("temp", "preview")
        os.makedirs(preview_dir, exist_ok=True)
        preview_path = os.path.join(preview_dir, "preview.png")
        preview_img.save(preview_path)

        pal_output = os.path.join(preview_dir, "palette.pal")
        with open(pal_output, "w") as f:
            f.write("JASC-PAL\n0100\n256\n")
            for r, g, b in full_palette:
                f.write(f"{int(r)} {int(g)} {int(b)}\n")

        if save_preview:
            os.makedirs("output", exist_ok=True)
            copy2(preview_path, os.path.join("output", "preview_image.png"))
            copy2(pal_output, os.path.join("output", "preview_palette.pal"))

    except Exception as e:
        print(translator.tr("error_preview", e=e))

