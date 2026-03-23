# core/image_utils.py
import os
import numpy as np
from PIL import Image
from shutil import copy2
from PySide6.QtGui import QImage
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from core.config import MARKER_COLOR
from core.config_manager import ConfigManager
from core.palette_utils import rgb_to_gba_rounded
from utils.translator import Translator
translator = Translator()


def analyze_tiles_bpp(image_path, tile_size=8):
    import numpy as np
    img = Image.open(image_path)
    if img.mode != 'P':
        return None
    width, height = img.size
    data = np.array(img)
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            tile = data[y:y + tile_size, x:x + tile_size]
            unique_indices = np.unique(tile)
            if len(unique_indices) > 16:
                return 8
            if len(np.unique(unique_indices // 16)) > 1:
                return 8
    return 4

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
    if pil_img.mode == "RGBA":
        data = pil_img.tobytes("raw", "RGBA")
        return QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
    else:
        rgb_img = pil_img.convert("RGB")
        data = rgb_img.tobytes("raw", "RGB")
        return QImage(data, rgb_img.size[0], rgb_img.size[1], QImage.Format_RGB888)

def create_gbagfx_preview(save_preview=False, keep_transparent=False):
    try:
        output_dir = "output"
        preview_dir = os.path.join("temp", "preview")
        os.makedirs(preview_dir, exist_ok=True)

        tiles_path = os.path.join(output_dir, "tiles.png")
        map_path = os.path.join(output_dir, "map.bin")

        if not os.path.exists(tiles_path) or not os.path.exists(map_path):
            from core.app_mode import is_gui_mode
            if not is_gui_mode():
                print(translator.tr("error_preview_missing_files"))
            return None

        config = ConfigManager()
        tilemap_width = int(config.get('CONVERSION', 'tilemap_width', '32'))
        tilemap_height = int(config.get('CONVERSION', 'tilemap_height', '32'))

        tc_str = config.get('CONVERSION', 'transparent_color', '0,0,0')
        transparent_color = tuple(map(int, tc_str.split(',')))

        palette_rgb = [(0, 0, 0)] * 256
        pal_files = sorted(f for f in os.listdir(output_dir)
                           if f.startswith('palette_') and f.endswith('.pal'))
        for pal_file in pal_files:
            stem = pal_file[len('palette_'):-len('.pal')]
            try:
                slot_or_index = int(stem)
                is_8bpp_pal = len(stem) == 3
                with open(os.path.join(output_dir, pal_file), 'r', encoding='utf-8') as pf:
                    plines = [l.strip() for l in pf
                              if l.strip() and not l.startswith(('JASC-PAL', '0100'))]
                count = int(plines[0])
                if is_8bpp_pal:
                    start = slot_or_index
                    for i in range(1, min(1 + count, len(plines))):
                        idx = start + (i - 1)
                        if idx < 256:
                            palette_rgb[idx] = tuple(map(int, plines[i].split()))
                    if keep_transparent:
                        tc = (
                            min(transparent_color[0] // 8 * 8, 248),
                            min(transparent_color[1] // 8 * 8, 248),
                            min(transparent_color[2] // 8 * 8, 248)
                        )
                        palette_rgb[0] = tc
                else:
                    slot = slot_or_index
                    for i in range(1, min(1 + count, len(plines))):
                        idx = slot * 16 + (i - 1)
                        if idx < 256:
                            palette_rgb[idx] = tuple(map(int, plines[i].split()))
            except Exception:
                pass

        with Image.open(tiles_path) as tiles_img:
            if tiles_img.mode != 'P':
                from core.app_mode import is_gui_mode
                if not is_gui_mode():
                    print(translator.tr("error_tiles_not_indexed"))
                return None
            tileset_data = np.array(tiles_img)
            ts_width_px, ts_height_px = tiles_img.size
            ts_width_tiles = ts_width_px // 8
            ts_height_tiles = ts_height_px // 8
            if not palette_rgb or all(c == (0,0,0) for c in palette_rgb):
                full_palette = tiles_img.getpalette()
                if full_palette:
                    for i in range(min(256, len(full_palette) // 3)):
                        palette_rgb[i] = (full_palette[i*3], full_palette[i*3+1], full_palette[i*3+2])

        with open(map_path, "rb") as f:
            map_bytes = f.read()
        
        num_entries = len(map_bytes) // 2
        total_tiles_needed = tilemap_width * tilemap_height

        if tilemap_width > 32 and tilemap_height >= 32:
            blocks_x = tilemap_width // 32
            blocks_y = tilemap_height // 32
            positions = [None] * total_tiles_needed
            idx = 0
            for by in range(blocks_y):
                for bx in range(blocks_x):
                    for ty in range(32):
                        for tx in range(32):
                            positions[idx] = ((bx * 32 + tx) * 8, (by * 32 + ty) * 8)
                            idx += 1
        else:
            positions = [
                ((i % tilemap_width) * 8, (i // tilemap_width) * 8)
                for i in range(total_tiles_needed)
            ]

        preview_array = np.zeros((tilemap_height * 8, tilemap_width * 8), dtype=np.uint8)

        for i in range(min(num_entries, total_tiles_needed)):
            entry = int.from_bytes(map_bytes[i*2:i*2+2], "little")
            tile_idx = entry & 0x03FF
            h_flip = (entry >> 10) & 1
            v_flip = (entry >> 11) & 1
            pal_slot = (entry >> 12) & 0xF

            if tile_idx >= ts_width_tiles * ts_height_tiles:
                continue

            tx = (tile_idx % ts_width_tiles) * 8
            ty = (tile_idx // ts_width_tiles) * 8

            tile_data = tileset_data[ty:ty+8, tx:tx+8].copy()
            if h_flip:
                tile_data = np.fliplr(tile_data)
            if v_flip:
                tile_data = np.flipud(tile_data)

            px, py = positions[i]
            
            preview_array[py:py+8, px:px+8] = tile_data + (pal_slot * 16)

        final_preview = Image.fromarray(preview_array, mode="P")

        flat_palette = []
        for r, g, b in palette_rgb:
            flat_palette.extend([r, g, b])
        
        while len(flat_palette) < 768:
            flat_palette.append(0)
        
        final_preview.putpalette(flat_palette)

        preview_path = os.path.join(preview_dir, "preview.png")
        final_preview.save(preview_path)

        pal_output = os.path.join(preview_dir, "palette.pal")
        with open(pal_output, "w", encoding='utf-8') as f:
            f.write("JASC-PAL\n0100\n256\n")
            for r, g, b in palette_rgb:
                f.write(f"{int(r)} {int(g)} {int(b)}\n")

        if save_preview:
            os.makedirs(output_dir, exist_ok=True)
            copy2(preview_path, os.path.join(output_dir, "preview_image.png"))
            copy2(pal_output, os.path.join(output_dir, "preview_palette.pal"))

        from core.app_mode import is_gui_mode
        if not is_gui_mode():
            print(translator.tr("preview_generated"))
        return preview_path

    except Exception as e:
        print(f"❌ Error generating preview.png: {e}")
        import traceback
        traceback.print_exc()
        return None
