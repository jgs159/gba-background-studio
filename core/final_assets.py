# core/final_assets.py
import os
import numpy as np
from PIL import Image
from collections import Counter
from core.config import MARKER_COLOR
from core.palette_utils import rgb_to_gba_rounded, group_consecutive_palettes
from core.image_utils import extract_tiles_rgba
from utils.translator import Translator
translator = Translator()


def reorganize_tilemap_for_gba_bg(tile_map, img_width, img_height):
    width_tiles  = img_width  // 8
    height_tiles = img_height // 8

    if width_tiles <= 32:
        return tile_map

    if width_tiles % 32 != 0 or height_tiles % 32 != 0:
        raise ValueError(
            f"GBA BG wider than 32 tiles requires both dimensions to be multiples of 32. "
            f"Got {width_tiles}x{height_tiles} tiles."
        )

    blocks_x = width_tiles  // 32
    blocks_y = height_tiles // 32

    reorganized = []
    for by in range(blocks_y):
        for bx in range(blocks_x):
            for ty in range(32):
                for tx in range(32):
                    idx = (by * 32 + ty) * width_tiles + (bx * 32 + tx)
                    reorganized.append(tile_map[idx] if idx < len(tile_map) else (0, 0, 0, 0))
    return reorganized

def revert_gba_tilemap_reorganization(tilemap_data, old_width_tiles, old_height_tiles, new_width_tiles, new_height_tiles):
    if old_width_tiles <= 32:
        return tilemap_data
    
    total_entries = len(tilemap_data) // 2
    new_total_entries = new_width_tiles * new_height_tiles
    
    blocks_x = old_width_tiles // 32
    blocks_y = old_height_tiles // 32
    
    reorganized_entries = [b'\x00\x00'] * new_total_entries
    
    for new_y in range(min(new_height_tiles, old_height_tiles)):
        for new_x in range(min(new_width_tiles, old_width_tiles)):
            block_x = new_x // 32
            block_y = new_y // 32
            
            if block_x < blocks_x and block_y < blocks_y:
                local_x = new_x % 32
                local_y = new_y % 32
                
                block_index = block_y * blocks_x + block_x
                local_index = local_y * 32 + local_x
                original_index = block_index * 1024 + local_index
                
                if original_index < total_entries:
                    start_byte = original_index * 2
                    entry = tilemap_data[start_byte:start_byte + 2]
                    
                    new_index = new_y * new_width_tiles + new_x
                    reorganized_entries[new_index] = entry
    
    new_data = bytearray()
    for entry in reorganized_entries:
        new_data.extend(entry)
    
    return bytes(new_data)

def _calc_tileset_cols(n):
    if n <= 0:
        return 1
    best_cols = n
    best_score = float('inf')
    for c in range(1, min(65, n + 1)):
        r = (n + c - 1) // c
        padding = c * r - n
        score = padding * 10 + abs(c - r) + (max(0, r - 32) * 10000)
        if c >= r:
            score -= 5
        if score < best_score:
            best_score = score
            best_cols = c
    return best_cols


def generate_final_assets_4bpp(img, pal_indices, selected_palettes, extra_transparent_tiles=0, tile_width=None):
    import os
    import numpy as np
    from PIL import Image

    img_w, img_h = img.size
    tiles_p = extract_tiles_rgba(img)
    n_tiles = len(tiles_p)

    using_real_indices = False
    if pal_indices and any(idx >= len(selected_palettes) for idx in pal_indices):
        using_real_indices = True
        real_palettes_in_use = sorted(set(pal_indices))

    palette_mapping = {}
    if using_real_indices:
        for real_idx in set(pal_indices):
            palette_mapping[real_idx] = real_idx
    else:
        for local_idx, real_idx in enumerate(selected_palettes):
            palette_mapping[local_idx] = real_idx

    unique_tiles = []
    tile_map = []
    seen = {}
    empty_tile = np.zeros((8, 8), dtype=np.uint8)
    empty_key = tuple(empty_tile.flatten())
    
    if using_real_indices and pal_indices:
        from collections import Counter
        palette_counter = Counter(pal_indices)
        empty_tile_palette = palette_counter.most_common(1)[0][0]
    else:
        empty_tile_palette = selected_palettes[0]
    
    unique_tiles.append(empty_tile)
    seen[empty_key] = (0, empty_tile_palette)

    for _group in range(extra_transparent_tiles):
        unique_tiles.append(empty_tile.copy())

    for i, tile_p in enumerate(tiles_p):
        tile_4bpp = np.array(tile_p)
        input_idx = pal_indices[i] if pal_indices is not None else 0
        
        if using_real_indices:
            real_pal_idx = input_idx
            if real_pal_idx not in palette_mapping:
                real_pal_idx = empty_tile_palette
        else:
            if input_idx in palette_mapping:
                real_pal_idx = palette_mapping[input_idx]
            else:
                real_pal_idx = empty_tile_palette

        t_original = tile_4bpp
        t_hflip = np.fliplr(t_original)
        t_vflip = np.flipud(t_original)
        t_hvflip = np.fliplr(t_vflip)

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
                stored_id, stored_real_pal_idx = seen[key]
                tile_map.append((stored_id, h, v, int(real_pal_idx)))
                matched = True
                break

        if not matched:
            new_id = len(unique_tiles)
            unique_tiles.append(t_original)
            key_orig = tuple(t_original.flatten())
            seen[key_orig] = (new_id, int(real_pal_idx))
            tile_map.append((new_id, 0, 0, int(real_pal_idx)))

    total_tiles = len(unique_tiles)
    if total_tiles > 1024:
        raise ValueError(translator.tr("error_tileset_too_big", n=total_tiles))

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    marker_gba = rgb_to_gba_rounded(MARKER_COLOR)
    indexed_dir = os.path.join("temp", "02_reindexed")

    for local_idx, real_pal_idx in enumerate(selected_palettes):
        group_path = os.path.join(indexed_dir, f"group_{local_idx}_indexed.png")
        
        if os.path.exists(group_path):
            with Image.open(group_path) as img_group:
                pal = img_group.getpalette()
            
            slot_palette = []
            for j in range(16):
                r = pal[j*3]
                g = pal[j*3+1]
                b = pal[j*3+2]
                r_gba, g_gba, b_gba = rgb_to_gba_rounded((r, g, b))
                
                if j == 0 and (r_gba, g_gba, b_gba) == marker_gba:
                    slot_palette.append((0, 0, 0))
                else:
                    slot_palette.append((r_gba, g_gba, b_gba))
            
            filename = f"palette_{real_pal_idx:02d}.pal"
            with open(os.path.join(output_dir, filename), "w") as f:
                f.write("JASC-PAL\n0100\n16\n")
                for r, g, b in slot_palette:
                    f.write(f"{r} {g} {b}\n")

    from core.app_mode import is_gui_mode
    if not is_gui_mode():
        print(translator.tr("palette_saved"))

    map_path = os.path.join(output_dir, "map.bin")
    reorganized = reorganized = reorganize_tilemap_for_gba_bg(tile_map, img_w, img_h)
    with open(map_path, "wb") as f:
        for idx, hflip, vflip, real_pal_idx in reorganized:
            entry = idx & 0x3FF
            if hflip: entry |= (1 << 10)
            if vflip: entry |= (1 << 11)
            entry |= (int(real_pal_idx) << 12)
            f.write(entry.to_bytes(2, 'little'))
    
    if not is_gui_mode():
        print(translator.tr("tilemap_saved"))

    n = total_tiles
    cols = tile_width if (tile_width is not None and 1 <= tile_width <= 64) else _calc_tileset_cols(n)
    rows = (n + cols - 1) // cols

    img_width = cols * 8
    img_height = rows * 8
    tiles_img = Image.new("P", (img_width, img_height))

    if len(selected_palettes) == 1:
        real_pal_idx = selected_palettes[0]
        group_path = os.path.join(indexed_dir, f"group_0_indexed.png")
        
        if os.path.exists(group_path):
            with Image.open(group_path) as img_with_palette:
                actual_palette = img_with_palette.getpalette()
            
            flat_palette = []
            for j in range(16):
                r = actual_palette[j*3]
                g = actual_palette[j*3+1] 
                b = actual_palette[j*3+2]
                r_gba, g_gba, b_gba = rgb_to_gba_rounded((r, g, b))
                flat_palette.extend([r_gba, g_gba, b_gba])
            
            while len(flat_palette) < 768:
                flat_palette.append(0)
                
            tiles_img.putpalette(flat_palette)
        else:
            flat_palette = []
            for i in range(16):
                level = int(i * 17)
                flat_palette.extend([level, level, level])
            while len(flat_palette) < 768:
                flat_palette.append(0)
            tiles_img.putpalette(flat_palette)
    else:
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

    real_unique = total_tiles - extra_transparent_tiles
    if not is_gui_mode():
        if extra_transparent_tiles > 0:
            print(translator.tr("process_completed_extra", real=real_unique, extra=extra_transparent_tiles, total=total_tiles))
            print(translator.tr("note_transparency"))
        else:
            print(translator.tr("process_completed", n=total_tiles))

    counts = {}
    for _x, _y, _z, real_pal_idx in tile_map:
        real_pal_int = int(real_pal_idx)
        counts[real_pal_int] = counts.get(real_pal_int, 0) + 1
    
    filtered_counts = {k: v for k, v in counts.items() if k in selected_palettes}
    sorted_counts = dict(sorted(filtered_counts.items()))
    
    if not is_gui_mode():
        print(translator.tr("local_palette_usage", counts=sorted_counts))

def generate_final_assets_rotation(img, extra_transparent_tiles=0, tile_width=None):
    img_w, img_h = img.size
    tiles = extract_tiles_rgba(img)
    n_tiles = len(tiles)

    from core.app_mode import is_gui_mode
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    raw_pal = img.getpalette()
    saved_palette = []
    for i in range(0, min(len(raw_pal), 768), 3):
        r, g, b = raw_pal[i], raw_pal[i+1], raw_pal[i+2]
        r_gba, g_gba, b_gba = rgb_to_gba_rounded((r, g, b))
        saved_palette.append((r_gba, g_gba, b_gba))
    pal_path = os.path.join(output_dir, "palette_016.pal")
    with open(pal_path, "w") as f:
        f.write("JASC-PAL\n0100\n")
        f.write(f"{len(saved_palette)}\n")
        for r, g, b in saved_palette:
            f.write(f"{int(r)} {int(g)} {int(b)}\n")

    unique_tiles = []
    tile_map = []
    seen = {}
    empty_tile = np.zeros((8, 8), dtype=np.uint8)
    empty_key = tuple(empty_tile.flatten())

    unique_tiles.append(empty_tile)
    seen[empty_key] = 0
    for _ in range(extra_transparent_tiles):
        unique_tiles.append(empty_tile.copy())

    for tile in tiles:
        tile_data = np.array(tile)
        key = tuple(tile_data.flatten())
        if key in seen:
            tile_map.append(seen[key])
        else:
            new_id = len(unique_tiles)
            if new_id > 255:
                raise ValueError(translator.tr("error_rotation_tileset_too_big", n=new_id + 1))
            unique_tiles.append(tile_data)
            seen[key] = new_id
            tile_map.append(new_id)

    total_tiles = len(unique_tiles)

    map_path = os.path.join(output_dir, "map.bin")
    with open(map_path, "wb") as f:
        for idx in tile_map:
            f.write(bytes([idx & 0xFF]))
    if not is_gui_mode():
        print(translator.tr("tilemap_saved"))

    n = total_tiles
    cols = tile_width if (tile_width is not None and 1 <= tile_width <= 64) else _calc_tileset_cols(n)
    rows = (n + cols - 1) // cols

    tiles_img = Image.new("P", (cols * 8, rows * 8))
    tiles_img.putpalette(img.getpalette())
    for idx, tile_data in enumerate(unique_tiles):
        x = (idx % cols) * 8
        y = (idx // cols) * 8
        tile_img = Image.fromarray(tile_data.astype(np.uint8), mode="P")
        tiles_img.paste(tile_img, (x, y))
    tiles_img.save(os.path.join(output_dir, "tiles.png"))

    if not is_gui_mode():
        print(translator.tr("process_completed", n=total_tiles))

def generate_final_assets_8bpp(img, start_index, palette_size, extra_transparent_tiles=0, tile_width=None):
    img_w, img_h = img.size
    tiles = extract_tiles_rgba(img)
    n_tiles = len(tiles)

    from core.app_mode import is_gui_mode
    if not is_gui_mode():
        print(translator.tr("extracting_palettes"), flush=True)
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
        r_gba, g_gba, b_gba = rgb_to_gba_rounded((r, g, b))
        saved_palette.append((r_gba, g_gba, b_gba))
        if len(saved_palette) >= palette_size:
            break

    with open(pal_path, "w") as f:
        f.write("JASC-PAL\n0100\n")
        f.write(f"{len(saved_palette)}\n")
        for r, g, b in saved_palette:
            f.write(f"{int(r)} {int(g)} {int(b)}\n")

    if not is_gui_mode():
        print(translator.tr("palette_saved"))

    if not is_gui_mode():
        print(translator.tr("generating_assets"), flush=True)
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
        raise ValueError(translator.tr("error_tileset_too_big", n=total_tiles))

    map_path = os.path.join(output_dir, "map.bin")
    tile_map_list = [tile_map[i] if i in tile_map else (0, 0, 0, 0) for i in range(n_tiles)]
    reorganized = reorganize_tilemap_for_gba_bg(tile_map_list, img_w, img_h)
    with open(map_path, "wb") as f:
        for tile_id, hflip, vflip, pal_idx in reorganized:
            entry = tile_id & 0x3FF
            if hflip: entry |= (1 << 10)
            if vflip: entry |= (1 << 11)
            entry |= (pal_idx << 12)
            f.write(entry.to_bytes(2, 'little'))
    if not is_gui_mode():
        print(translator.tr("tilemap_saved"))

    n = total_tiles
    cols = tile_width if (tile_width is not None and 1 <= tile_width <= 64) else _calc_tileset_cols(n)
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

    real_unique = total_tiles - extra_transparent_tiles
    if not is_gui_mode():
        if extra_transparent_tiles > 0:
            print(translator.tr("process_completed_extra", real=real_unique, extra=extra_transparent_tiles, total=total_tiles))
        else:
            print(translator.tr("process_completed", n=total_tiles))
