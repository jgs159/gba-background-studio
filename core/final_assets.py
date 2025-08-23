# core/final_assets.py
import os
import numpy as np
from PIL import Image
from collections import Counter
from core.config import MARKER_COLOR
from core.palette_utils import rgb_to_gba_rounded
from core.image_utils import extract_tiles_rgba
from core.tile_utils import group_consecutive_palettes
from core.language import translate


def generate_final_assets_4bpp(img, pal_indices, selected_palettes, extra_transparent_tiles=0, tile_width=None):
    """
    Genera los archivos finales para modo 4bpp:
        - output/tiles.png
        - output/map.bin
        - output/palette_xx.pal
    """
    w, h = img.size
    tiles_p = extract_tiles_rgba(img)
    n_tiles = len(tiles_p)

    # === Detección de tiles únicos con H/V flip ===
    unique_tiles = []
    tile_map = []
    seen = {}
    empty_tile = np.zeros((8, 8), dtype=np.uint8)
    empty_key = tuple(empty_tile.flatten())
    unique_tiles.append(empty_tile)
    seen[empty_key] = (0, 0)

    for _group in range(extra_transparent_tiles):
        unique_tiles.append(empty_tile.copy())

    for i, tile_p in enumerate(tiles_p):
        tile_4bpp = np.array(tile_p)
        local_idx = pal_indices[i]
        if local_idx < len(selected_palettes):
            pal_idx = selected_palettes[local_idx]
        else:
            pal_idx = selected_palettes[0]

        t_original = tile_4bpp
        t_hflip = np.fliplr(t_original)
        t_vflip = np.flipud(t_original)
        t_hvflip = np.fliplr(t_vflip)

        # === Priorizar: original → hflip → vflip → hvflip ===
        candidates = [
            (t_original, 0, 0),
            (t_hflip,    1, 0),
            (t_vflip,    0, 1),
            (t_hvflip,   1, 1),
        ]

        matched = False
        for t, h, v in candidates:
            key = tuple(t.flatten())
            if key in seen:
                stored_id, stored_pal = seen[key]
                tile_map.append((stored_id, h, v, stored_pal))
                matched = True
                break

        if not matched:
            new_id = len(unique_tiles)
            unique_tiles.append(t_original)
            key_orig = tuple(t_original.flatten())
            seen[key_orig] = (new_id, pal_idx)
            tile_map.append((new_id, 0, 0, pal_idx))

    total_tiles = len(unique_tiles)
    if total_tiles > 1024:
        print(translate("error_tileset_too_big", n=total_tiles))
        sys.exit(1)

    # === Directorio de salida ===
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # === Guardar paletas agrupadas (palette_XX.pal) ===
    groups = group_consecutive_palettes(selected_palettes)
    marker_gba = rgb_to_gba_rounded(MARKER_COLOR)

    indexed_dir = os.path.join("temp", "02_reindexed")
    for base_idx, count in groups:
        combined_palette = []
        for i in range(count):
            real_pal_idx = base_idx + i
            if real_pal_idx in selected_palettes:
                group_path = os.path.join(indexed_dir, f"group_{selected_palettes.index(real_pal_idx)}_indexed.png")
                if os.path.exists(group_path):
                    img = Image.open(group_path)
                    pal = img.getpalette()
                    for j in range(16):
                        r = pal[j*3]
                        g = pal[j*3+1]
                        b = pal[j*3+2]
                        combined_palette.append((r, g, b))
                else:
                    combined_palette.extend([(0,0,0)] * 16)
            else:
                combined_palette.extend([(0,0,0)] * 16)
        while len(combined_palette) < count * 16:
            combined_palette.append((0,0,0))

        # Ajustar índice 0: si es MARKER_COLOR, reemplazar
        for i in range(0, len(combined_palette), 16):
            if rgb_to_gba_rounded(combined_palette[i]) == marker_gba:
                combined_palette[i] = (0, 0, 0)

        filename = f"palette_{base_idx:02d}.pal"
        with open(os.path.join(output_dir, filename), "w") as f:
            f.write("JASC-PAL\n0100\n")
            f.write(f"{len(combined_palette)}\n")
            for r, g, b in combined_palette:
                f.write(f"{r} {g} {b}\n")
    print(translate("palette_saved"))

    # === Guardar tilemap.bin ===
    map_path = os.path.join(output_dir, "map.bin")
    with open(map_path, "wb") as f:
        for idx, hflip, vflip, pal_idx in tile_map:
            entry = idx & 0x3FF
            if hflip: entry |= (1 << 10)
            if vflip: entry |= (1 << 11)
            entry |= (pal_idx << 12)
            f.write(entry.to_bytes(2, 'little'))
    print(translate("tilemap_saved"))

    # === Generar tiles.png ===
    n = total_tiles
    if tile_width is not None and 1 <= tile_width <= 64:
        cols = tile_width
    else:
        best_cols = 1
        best_score = float('inf')
        for c in range(1, min(65, n + 1)):
            r = (n + c - 1) // c
            if r > 32:
                continue
            if c < r:
                continue
            padding = c * r - n
            if padding > 4:
                continue
            score = padding * 100 + abs(c - r)
            if c > r:
                score -= 100
            if c >= r:
                score -= 50
            if score < best_score:
                best_score = score
                best_cols = c
        if best_score == float('inf'):
            for c in range(1, min(65, n + 1)):
                r = (n + c - 1) // c
                if c < r:
                    continue
                padding = c * r - n
                score = padding * 100 + abs(c - r) + (max(0, r - 32) * 1000)
                if c > r:
                    score -= 100
                if score < best_score:
                    best_score = score
                    best_cols = c
        cols = best_cols

    rows = (n + cols - 1) // cols
    if rows > 32:
        rows = 32
        cols = (n + rows - 1) // rows

    img_width = cols * 8
    img_height = rows * 8
    tiles_img = Image.new("P", (img_width, img_height))

    flat_palette = []
    for i in range(16):
        level = int(i * 17)
        flat_palette.extend([level, level, level])
    while len(flat_palette) < 768:
        flat_palette.append(0)
    tiles_img.putpalette(flat_palette)

    for idx, tile_data in enumerate(unique_tiles):
        x = (idx % cols) * 8
        y = (idx // cols) * 8
        tile_img = Image.fromarray(tile_data.astype(np.uint8), mode="P")
        tiles_img.paste(tile_img, (x, y))

    tiles_path = os.path.join(output_dir, "tiles.png")
    tiles_img.save(tiles_path)

    # === Mensaje final ===
    real_unique = total_tiles - extra_transparent_tiles
    if extra_transparent_tiles > 0:
        print(translate("process_completed_extra", real=real_unique, extra=extra_transparent_tiles, total=total_tiles))
        print(translate("note_transparency"))
    else:
        print(translate("process_completed", n=total_tiles))

    counts = {}
    for _x, _y, _z, pal_idx in tile_map:
        counts[pal_idx] = counts.get(pal_idx, 0) + 1
    sorted_counts = dict(sorted(counts.items()))
    print(translate("local_palette_usage", counts=sorted_counts))

def generate_final_assets_8bpp(img, start_index, palette_size, extra_transparent_tiles=0, tile_width=None):
    w, h = img.size
    tiles = extract_tiles_rgba(img)
    n_tiles = len(tiles)

    # === 1. Guardar paleta final ===
    print(translate("extracting_palettes"), flush=True)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    pal_filename = f"palette_{start_index:03d}.pal"
    pal_path = os.path.join(output_dir, pal_filename)

    raw_pal = img.getpalette()
    saved_palette = []
    start_byte = start_index * 3

    for i in range(start_byte, len(raw_pal), 3):
        if i + 2 >= len(raw_pal):
            break
        r, g, b = raw_pal[i], raw_pal[i+1], raw_pal[i+2]
        saved_palette.append((r, g, b))
        if len(saved_palette) >= palette_size:
            break

    with open(pal_path, "w") as f:
        f.write("JASC-PAL\n0100\n")
        f.write(f"{len(saved_palette)}\n")
        for r, g, b in saved_palette:
            f.write(f"{int(r)} {int(g)} {int(b)}\n")
    print(translate("palette_saved"))

    # === 2. Detección de tiles únicos con H/V flip ===
    print(translate("generating_assets"), flush=True)
    unique_tiles = []
    tile_map = {}
    seen = {}
    empty_tile = np.zeros((8, 8), dtype=np.uint8)
    empty_key = tuple(empty_tile.flatten())

    unique_tiles.append(empty_tile)
    seen[empty_key] = 0
    unique_tiles.extend([empty_tile.copy() for _ in range(extra_transparent_tiles)])

    for i, tile in enumerate(extract_tiles_rgba(img)):
        tile_data = np.array(tile)
        
        t_original = tile_data
        t_hflip = np.fliplr(t_original)
        t_vflip = np.flipud(t_original)
        t_hvflip = np.fliplr(t_vflip)

        # === Priorizar: original → hflip → vflip → hvflip ===
        candidates = [
            (t_original, 0, 0),
            (t_hflip,    1, 0),
            (t_vflip,    0, 1),
            (t_hvflip,   1, 1),
        ]

        matched = False
        for t, h, v in candidates:
            key = tuple(t.flatten())
            if key in seen:
                tile_map[i] = (seen[key], h, v, 0)
                matched = True
                break

        if not matched:
            new_id = len(unique_tiles)
            unique_tiles.append(t_original.copy())
            key_orig = tuple(t_original.flatten())
            seen[key_orig] = new_id
            tile_map[i] = (new_id, 0, 0, 0)

    total_tiles = len(unique_tiles)
    if total_tiles > 1024:
        print(translate("error_tileset_too_big", n=total_tiles))
        sys.exit(1)

    # === 3. Guardar tilemap.bin ===
    map_path = os.path.join(output_dir, "map.bin")
    with open(map_path, "wb") as f:
        for i in range(n_tiles):
            tile_id, hflip, vflip, pal_idx = tile_map[i]
            entry = tile_id & 0x3FF
            if hflip: entry |= (1 << 10)
            if vflip: entry |= (1 << 11)
            entry |= (pal_idx << 12)
            f.write(entry.to_bytes(2, 'little'))
    print(translate("tilemap_saved"))

    # === 4. Generar tiles.png ===
    n = total_tiles
    if tile_width is not None and 1 <= tile_width <= 64:
        cols = tile_width
    else:
        best_cols = 1
        best_score = float('inf')
        for c in range(1, min(65, n + 1)):
            r = (n + c - 1) // c
            # Limitar el alto máximo a 32 tiles
            if r > 32:
                continue
            # Asegurar que el ancho sea mayor o igual al alto
            if c < r:
                continue
            padding = c * r - n
            if padding > 4:
                continue
            score = padding * 100 + abs(c - r)
            if c > r:
                score -= 100
            if c >= r:
                score -= 50
            if score < best_score:
                best_score = score
                best_cols = c
        
        if best_score == float('inf'):
            for c in range(1, min(65, n + 1)):
                r = (n + c - 1) // c
                if c < r:
                    continue
                padding = c * r - n
                score = padding * 100 + abs(c - r) + (max(0, r - 32) * 1000)
                if c > r:
                    score -= 100
                if score < best_score:
                    best_score = score
                    best_cols = c

    cols = best_cols
    rows = (n + cols - 1) // cols
    img_width = cols * 8
    img_height = rows * 8

    tiles_img = Image.new("P", (img_width, img_height))
    tiles_img.putpalette(img.getpalette())

    for idx, tile_data in enumerate(unique_tiles):
        x = (idx % cols) * 8
        y = (idx // cols) * 8
        tile_img = Image.fromarray(tile_data.astype(np.uint8), mode="P")
        tiles_img.paste(tile_img, (x, y))

    tiles_path = os.path.join(output_dir, "tiles.png")
    tiles_img.save(tiles_path)

    # === Mensaje final ===
    real_unique = total_tiles - extra_transparent_tiles
    if extra_transparent_tiles > 0:
        print(translate("process_completed_extra", real=real_unique, extra=extra_transparent_tiles, total=total_tiles))
    else:
        print(translate("process_completed", n=total_tiles))
