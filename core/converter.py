# -*- coding: utf-8 -*-
import os
import sys
import argparse
import subprocess
import numpy as np
from PIL import Image
import shutil
import configparser

# === Suppress joblib warnings ===
os.environ['JOBLIB_WORKER_COUNT'] = '4'
os.environ['JOBLIB_MULTIPROCESSING'] = '0'
os.environ['LOKY_MAX_CPU_COUNT'] = '4'

# === Marker color in GBA format (248, 0, 248) → bright magenta ===
MARKER_COLOR = (248, 0, 248)  # GBA 15-bit

# === Language setting (3-letter code) ===
LANGUAGE = "eng"  # Options: eng, spa, brp, fra, deu, ita, por, ind, hin, rus, jpn, cmn

# === Load language file from lang/ folder ===
_lang = configparser.ConfigParser()
lang_file = f"lang/{LANGUAGE}.ini"
if not os.path.exists(lang_file):
    print(f"❌ Language file not found: {lang_file}")
    sys.exit(1)

try:
    _lang.read(lang_file, encoding='utf-8')
except Exception as e:
    print(f"❌ Error reading language file {lang_file}: {e}")
    sys.exit(1)

def _(key, **kwargs):
    """Translate and format a message."""
    text = _lang.get("lang", key, fallback=f"MISSING: {key}")
    return text.format(**kwargs)

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

def rgb_to_gba_rounded(color):
    r, g, b = color
    return (
        min((r + 4) // 8 * 8, 255),
        min((g + 4) // 8 * 8, 255),
        min((b + 4) // 8 * 8, 255)
    )

def replace_transparent_with_marker(img, transparent_color):
    """
    Replaces all pixels with `transparent_color` by `MARKER_COLOR`.
    """
    arr = np.array(img)
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    opaque = a > 128

    mask = (r == transparent_color[0]) & (g == transparent_color[1]) & (b == transparent_color[2]) & opaque
    count = np.sum(mask)

    if count > 0:
        arr[mask, 0] = MARKER_COLOR[0]
        arr[mask, 1] = MARKER_COLOR[1]
        arr[mask, 2] = MARKER_COLOR[2]

    return Image.fromarray(arr.astype(np.uint8)), count

def split_into_groups(input_path, tilemap_path, output_dir="temp", use_tilemap=False, num_palettes=1):
    img = Image.open(input_path)
    if img.mode != 'RGBA':
        img = img.convert("RGBA")
    w, h = img.size
    w = (w // 8) * 8
    h = (h // 8) * 8
    img = img.crop((0, 0, w, h))
    tiles = extract_tiles_rgba(img)
    n_tiles = len(tiles)

    if use_tilemap:
        if not os.path.exists(tilemap_path):
            raise FileNotFoundError(f"Tilemap not found: {tilemap_path}")
        with open(tilemap_path, 'rb') as f:
            data = f.read()
        if len(data) % 2 != 0:
            raise ValueError("Tilemap must have even length.")
        if len(data) // 2 != n_tiles:
            raise ValueError("Tilemap length does not match number of tiles.")
        pal_indices = [(data[i] | (data[i+1] << 8)) >> 12 & 0xF for i in range(0, len(data), 2)]
    else:
        from sklearn.cluster import KMeans
        features = []
        for tile in tiles:
            arr = np.array(tile)
            r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
            opaque = a > 128
            valid_pixels = opaque & ~(
                (r == MARKER_COLOR[0]) & (g == MARKER_COLOR[1]) & (b == MARKER_COLOR[2])
            )
            pixels = arr[valid_pixels][:, :3]
            if len(pixels) > 0:
                mean = np.mean(pixels, axis=0)
                features.append(mean)

        if len(features) == 0:
            pal_indices = [0] * n_tiles
        else:
            X = np.array(features)
            n_clusters = min(num_palettes, len(X))
            km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
            labels = km.fit_predict(X)
            pal_indices = [0] * n_tiles
            j = 0
            for i in range(n_tiles):
                arr = np.array(tiles[i])
                r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
                opaque = a > 128
                valid_pixels = opaque & ~(
                    (r == MARKER_COLOR[0]) & (g == MARKER_COLOR[1]) & (b == MARKER_COLOR[2])
                )
                if np.any(valid_pixels):
                    pal_indices[i] = labels[j] % num_palettes
                    j += 1

    os.makedirs(output_dir, exist_ok=True)
    width_in_tiles = w // 8

    for pal_idx in range(num_palettes):
        group_img = Image.new("RGBA", (w, h), (*MARKER_COLOR, 255))
        modified = False
        for i, tile in enumerate(tiles):
            ty = (i // width_in_tiles) * 8
            tx = (i % width_in_tiles) * 8
            if pal_indices[i] == pal_idx:
                group_img.paste(tile, (tx, ty))
                modified = True
        if modified:
            path = os.path.join(output_dir, f"group_{pal_idx}.png")
            group_img.save(path)

    return output_dir, pal_indices

def ensure_gba_black_at_index_0(png_path, pal_path, reindexed_path, irfanview_path, lang_section=None):
    try:
        img = Image.open(png_path)
        if img.mode != 'P':
            return

        palette = img.getpalette()
        rgb_palette = []
        for i in range(16):
            r = palette[i*3]
            g = palette[i*3+1]
            b = palette[i*3+2]
            rgb_palette.append((r, g, b))

        gba_palette = [rgb_to_gba_rounded(c) for c in rgb_palette]
        marker_gba = rgb_to_gba_rounded(MARKER_COLOR)

        if gba_palette[0] == marker_gba:
            import shutil
            shutil.copy2(png_path, reindexed_path)
            return

        candidate_idx = -1
        for i, c in enumerate(gba_palette):
            if c == marker_gba:
                candidate_idx = i
                break

        if candidate_idx == -1:
            new_rgb_palette = [marker_gba] + rgb_palette[:15]
        else:
            new_rgb_palette = [rgb_palette[candidate_idx]]
            for i, c in enumerate(rgb_palette):
                if i != candidate_idx and len(new_rgb_palette) < 16:
                    new_rgb_palette.append(c)
            while len(new_rgb_palette) < 16:
                new_rgb_palette.append(new_rgb_palette[-1])

        with open(pal_path, 'w') as f:
            f.write("JASC-PAL\n0100\n16\n")
            for r, g, b in new_rgb_palette:
                f.write(f"{r} {g} {b}\n")

        cmd = [
            irfanview_path,
            png_path,
            f"/import_pal={pal_path}",
            f"/convert={reindexed_path}"
        ]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            import shutil
            shutil.copy2(png_path, reindexed_path)
        else:
            print(_("indexed_with_palette", path=reindexed_path))

    except Exception as e:
        print(_("error_ensure_gba", e=e))
        import shutil
        shutil.copy2(png_path, reindexed_path)

def quantize_with_irfanview(groups_dir, irfanview_path="C:\\Program Files\\IrfanView\\i_view64.exe"):
    indexed_dir = os.path.join(groups_dir, "01_indexed")
    reindexed_dir = os.path.join(groups_dir, "02_reindexed")
    os.makedirs(indexed_dir, exist_ok=True)
    os.makedirs(reindexed_dir, exist_ok=True)

    for i in range(16):
        input_path = os.path.abspath(os.path.join(groups_dir, f"group_{i}.png"))
        if not os.path.exists(input_path):
            continue

        output_1 = os.path.abspath(os.path.join(indexed_dir, f"group_{i}_indexed.png"))
        cmd1 = [
            irfanview_path,
            input_path,
            "/bpp=4",
            "/dither=0",
            f"/convert={output_1}"
        ]
        result = subprocess.run(cmd1)
        if result.returncode != 0:
            continue

        pal_path = os.path.abspath(os.path.join(reindexed_dir, f"group_{i}_palette.pal"))
        output_2 = os.path.abspath(os.path.join(reindexed_dir, f"group_{i}_indexed.png"))
        ensure_gba_black_at_index_0(output_1, pal_path, output_2, irfanview_path)

    return reindexed_dir

def apply_gba_palette_format(indexed_dir):
    """
    Converts palette of each image to GBA 15-bit format.
    """
    for i in range(16):
        path = os.path.join(indexed_dir, f"group_{i}_indexed.png")
        if not os.path.exists(path):
            continue
        try:
            img = Image.open(path)
            if img.mode != 'P':
                continue
            pal = img.getpalette()
            rgb_pal = [(pal[j*3], pal[j*3+1], pal[j*3+2]) for j in range(16)]
            gba_pal = [rgb_to_gba_rounded(c) for c in rgb_pal]

            flat_gba = []
            for r, g, b in gba_pal:
                flat_gba.extend([r, g, b])
            while len(flat_gba) < 768:
                flat_gba.append(0)

            img.putpalette(flat_gba)
            img.save(path)
        except Exception as e:
            print(_("error_apply_gba_palette", i=i, e=e))

def extract_palettes_from_indexed(indexed_dir, num_palettes=16):
    palettes = []
    for i in range(num_palettes):
        path = os.path.join(indexed_dir, f"group_{i}_indexed.png")
        if not os.path.exists(path):
            palettes.append([(0,0,0)] * 16)
            continue
        img = Image.open(path)
        if img.mode != 'P':
            img = img.convert('P', palette=Image.ADAPTIVE, colors=16)
        pil_pal = img.getpalette()
        rgb_pal = []
        for j in range(16):
            r = pil_pal[j*3]
            g = pil_pal[j*3+1]
            b = pil_pal[j*3+2]
            rgb_pal.append((r, g, b))
        palettes.append(rgb_pal)
    return palettes

def rebuild_final_image(input_path, pal_indices, indexed_dir, palettes, output_path="reconstructed.png"):
    img = Image.open(input_path)
    if img.mode != 'RGBA':
        img = img.convert("RGBA")
    w, h = img.size
    w = (w // 8) * 8
    h = (h // 8) * 8
    img = img.crop((0, 0, w, h))
    tiles = extract_tiles_rgba(img)
    n_tiles = len(tiles)

    indexed_tiles = {}
    for pal_idx in range(len(palettes)):
        group_path = os.path.join(indexed_dir, f"group_{pal_idx}_indexed.png")
        if os.path.exists(group_path):
            group_img = Image.open(group_path)
            indexed_tiles[pal_idx] = extract_tiles_rgba(group_img)
        else:
            indexed_tiles[pal_idx] = [Image.new("P", (8, 8), 0)] * n_tiles

    final_img = Image.new("P", (w, h))
    palette_96 = [color for pal in palettes for color in pal]
    flat_palette = sum(palette_96, ())
    final_img.putpalette(flat_palette)

    width_in_tiles = w // 8
    for i, tile_rgba in enumerate(tiles):
        pal_idx = pal_indices[i]
        if pal_idx in indexed_tiles and i < len(indexed_tiles[pal_idx]):
            tile_p = indexed_tiles[pal_idx][i]
            tx = (i % width_in_tiles) * 8
            ty = (i // width_in_tiles) * 8
            final_img.paste(tile_p, (tx, ty))

    final_img.save(output_path)
    return final_img

def create_gbagfx_preview(unique_tiles, output_file, max_width=64, max_height=16, max_padding=4, tile_width=None):
    if not unique_tiles:
        return
    n = len(unique_tiles)
    if n == 0:
        return

    if tile_width is not None:
        if not (1 <= tile_width <= 64):
            cols = min(64, n)
            rows = (n + cols - 1) // cols
        else:
            cols = tile_width
            rows = (n + cols - 1) // cols
    else:
        best = None
        best_score = float('inf')
        for c in range(1, min(65, n + max_padding + 1)):
            r = (n + c - 1) // c
            if r > max_height:
                continue
            padding = c * r - n
            if padding > max_padding:
                continue
            diff = abs(c - r)
            score = padding * 1000 + diff
            if c >= r:
                score -= 100
            if score < best_score:
                best_score = score
                best = (c, r)
        if best is None:
            cols = min(64, n)
            rows = (n + cols - 1) // cols
        else:
            cols, rows = best

    img_width = cols * 8
    img_height = rows * 8
    preview = Image.new("P", (img_width, img_height))
    palette_16gray = []
    for i in range(16):
        level = int(i * 17)
        palette_16gray.extend([level, level, level])
    while len(palette_16gray) < 768:
        palette_16gray.append(0)
    preview.putpalette(palette_16gray)
    for idx, tile in enumerate(unique_tiles):
        x = (idx % cols) * 8
        y = (idx // cols) * 8
        tile_img = Image.fromarray(tile.astype(np.uint8))
        preview.paste(tile_img, (x, y))
    preview.save(output_file)
    padding = cols * rows - n
    print(_("tileset_saved", n=n, padding=padding))

def generate_final_assets(reconstructed_img, pal_indices, palettes, start_index=0, extra_transparent_tiles=0, tile_width=None, transparent_color=(0,0,0), keep_transparent=False):
    w, h = reconstructed_img.size
    tiles_p = extract_tiles_rgba(reconstructed_img)
    n_tiles = len(tiles_p)

    unique_tiles = []
    tile_map = []
    seen = {}

    empty_tile = np.zeros((8, 8), dtype=np.uint8)
    empty_key = tuple(empty_tile.flatten())

    unique_tiles.append(empty_tile)
    seen[empty_key] = (0, 0)

    for i in range(extra_transparent_tiles):
        unique_tiles.append(empty_tile.copy())

    for i, tile_p in enumerate(tiles_p):
        tile_4bpp = np.array(tile_p)
        pal_idx = pal_indices[i]

        t_orig = tile_4bpp
        candidates = [
            (t_orig, 0, 0),
            (np.fliplr(t_orig), 1, 0),
            (np.flipud(t_orig), 0, 1),
            (np.fliplr(np.flipud(t_orig)), 1, 1),
        ]

        matched = False
        for t, hflip, vflip in candidates:
            key = tuple(t.flatten())
            if key in seen:
                stored_id, stored_pal = seen[key]
                tile_map.append((stored_id, hflip, vflip, pal_idx))
                matched = True
                break

        if not matched:
            new_id = len(unique_tiles)
            unique_tiles.append(t_orig.copy())
            seen[key] = (new_id, pal_idx)
            tile_map.append((new_id, 0, 0, pal_idx))

    total_tiles = len(unique_tiles)
    if total_tiles > 1024:
        print(_("error_tileset_too_big", n=total_tiles))
        sys.exit(1)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    raw_palette = [color for pal in palettes for color in pal]
    final_palette = raw_palette.copy()

    transparent_color_gba = rgb_to_gba_rounded(transparent_color)
    marker_gba = rgb_to_gba_rounded(MARKER_COLOR)

    for i in range(0, len(final_palette), 16):
        if i < len(final_palette):
            if keep_transparent:
                if final_palette[i] == marker_gba:
                    final_palette[i] = transparent_color_gba
            else:
                if final_palette[i] == marker_gba:
                    final_palette[i] = (0, 0, 0)

    with open(os.path.join(output_dir, "palette.pal"), "w") as f:
        f.write("JASC-PAL\n0100\n")
        f.write(f"{len(final_palette)}\n")
        for r, g, b in final_palette:
            f.write(f"{r} {g} {b}\n")
    print(_("palette_saved"))

    tilemap_entries = []
    for idx, hflip, vflip, pal_idx in tile_map:
        entry = idx & 0x3FF
        if hflip: entry |= (1 << 10)
        if vflip: entry |= (1 << 11)
        entry |= ((start_index + pal_idx) << 12)
        tilemap_entries.append(entry)

    with open(os.path.join(output_dir, "map.bin"), "wb") as f:
        for e in tilemap_entries:
            f.write(int(e).to_bytes(2, 'little'))
    print(_("tilemap_saved"))

    create_gbagfx_preview(unique_tiles, os.path.join(output_dir, "tiles.png"), tile_width=tile_width)

    from collections import Counter
    counts = Counter(int(pal) for _,_,_,pal in tile_map)
    sorted_counts = dict(sorted(counts.items()))
    print(_("local_palette_usage", counts=sorted_counts))

    real_unique = total_tiles - extra_transparent_tiles
    if extra_transparent_tiles > 0:
        print(_("process_completed_extra", real=real_unique, extra=extra_transparent_tiles, total=total_tiles))
        print(_("note_transparency"))
    else:
        print(_("process_completed", n=total_tiles))

    return final_palette
 
def generate_preview_image(reconstructed_path, groups_dir, transparent_color, output_path="output/preview.png"):
    try:
        base = Image.open(reconstructed_path).convert("RGBA")
        w, h = base.size
        indexed_dir = os.path.join(groups_dir, "02_reindexed")
        result = base.copy()

        group_0_path = os.path.join(indexed_dir, "group_0_indexed.png")
        if os.path.exists(group_0_path):
            group_0 = Image.open(group_0_path).convert("RGBA")
            result = Image.alpha_composite(result, group_0)

        for pal_idx in range(1, 16):
            group_path = os.path.join(indexed_dir, f"group_{pal_idx}_indexed.png")
            if not os.path.exists(group_path):
                continue
            overlay = Image.open(group_path).convert("RGBA")
            arr = np.array(overlay)
            r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

            mask = (r != 248) | (g != 0) | (b != 248)

            valid = np.zeros_like(arr)
            valid[mask] = arr[mask]
            valid_img = Image.fromarray(valid)

            result = Image.alpha_composite(result, valid_img)

        result = result.convert("P", palette=Image.ADAPTIVE, colors=256)
        transparent_color_gba = rgb_to_gba_rounded(transparent_color)
        marker_gba = rgb_to_gba_rounded(MARKER_COLOR)
        palette = result.getpalette()
        new_palette = palette[:]

        found = False
        for i in range(0, len(palette), 3):
            r = palette[i]
            g = palette[i+1]
            b = palette[i+2]
            if (r, g, b) == marker_gba:
                if keep_transparent:
                    new_palette[i] = transparent_color_gba[0]
                    new_palette[i+1] = transparent_color_gba[1]
                    new_palette[i+2] = transparent_color_gba[2]
                else:
                    new_palette[i] = 0
                    new_palette[i+1] = 0
                    new_palette[i+2] = 0
                found = True
                break

        result.putpalette(new_palette)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        result.save(output_path)
        print(_("preview_generated", path=output_path))
    except Exception as e:
        print(_("error_preview", e=e))


def main(input_path, tilemap_path=None, start_index=0, num_palettes=1, transparent_color=(0,0,0), extra_transparent_tiles=0, tile_width=None, origin=None, end=None, output_size=None, keep_temp=False, keep_transparent=False):
    use_tilemap = tilemap_path is not None

    # === Validate ranges ===
    if not (1 <= num_palettes <= 16):
        print(_("error_num_palettes"))
        sys.exit(1)

    if not (0 <= start_index <= 15):
        print(_("error_start_index"))
        sys.exit(1)

    PRESET_SIZES = {
        "screen": (256, 160),
        "bg0": (256, 256),
        "bg1": (512, 256),
        "bg2": (256, 512),
        "bg3": (512, 512),
    }

    try:
        img = Image.open(input_path)
        w, h = img.size
    except Exception as e:
        print(_("error_loading_image", e=e))
        sys.exit(1)

    def parse_coord(value, size=None):
        if value is None:
            return None
        value = str(value).strip("[]() ")
        if value.endswith("t"):
            try:
                return int(value[:-1]) * 8
            except:
                return None
        if value == "end":
            return size
        if value.startswith("end"):
            try:
                offset = int(value[3:])
                return size + offset if size is not None else None
            except:
                return None
        try:
            return int(value)
        except:
            return None

    def parse_pair(value, img_w=None, img_h=None):
        if value is None:
            return None
        try:
            value = value.strip("[]() ")
            x_str, y_str = value.split(",", 1)
            x = parse_coord(x_str.strip(), img_w)
            y = parse_coord(y_str.strip(), img_h)
            return (x, y) if x is not None and y is not None else None
        except:
            return None

    origin_parsed = parse_pair(origin, w, h) if origin else (0, 0)
    end_parsed = parse_pair(end, w, h) if end else None

    def parse_size(value):
        if value is None:
            return None
        value = value.strip()
        if value in PRESET_SIZES:
            return PRESET_SIZES[value]
        value = value.strip("()[]\"'")
        try:
            a, b = value.split(",", 1)
            a = a.strip()
            b = b.strip()
            wa = int(a[:-1]) * 8 if a.endswith("t") else int(a)
            wb = int(b[:-1]) * 8 if b.endswith("t") else int(b)
            return (wa, wb)
        except:
            return None

    output_size_parsed = parse_size(output_size)

    if origin_parsed is None:
        print(_("error_invalid_origin", origin=origin))
        sys.exit(1)
    orig_x, orig_y = origin_parsed

    if orig_x < 0 or orig_y < 0 or orig_x >= w or orig_y >= h:
        print(_("error_origin_out_of_bounds", x=orig_x, y=orig_y, w=w, h=h))
        sys.exit(1)

    # === Validate conflict ===
    if end_parsed and output_size_parsed:
        print(_("error_end_and_output_size"))
        sys.exit(1)

    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    cropped_img = None

    if end_parsed is not None:
        fin_x, fin_y = end_parsed
        crop_w = ((fin_x - orig_x) // 8) * 8
        crop_h = ((fin_y - orig_y) // 8) * 8
        if crop_w <= 0 or crop_h <= 0:
            print(_("error_crop_too_small"))
            sys.exit(1)
        end_x = orig_x + crop_w
        end_y = orig_y + crop_h
        cropped_img = img.crop((orig_x, orig_y, min(end_x, w), min(end_y, h)))

    elif output_size_parsed is not None:
        target_w, target_h = output_size_parsed
        end_x = orig_x + target_w
        end_y = orig_y + target_h
        if end_x > w or end_y > h:
            print(_("error_crop_exceeds", w=end_x, h=end_y, aw=w, ah=h))
            sys.exit(1)
        cropped_img = img.crop((orig_x, orig_y, end_x, end_y))

    else:
        if w > 512 or h > 512:
            print(_("error_image_too_big"))
            sys.exit(1)
        if w % 8 != 0 or h % 8 != 0:
            print(_("error_dimensions_not_multiple"))
            sys.exit(1)
        cropped_img = img.copy()
        print(_("image_valid", w=w, h=h))

    if output_size_parsed:
        target_w, target_h = output_size_parsed
        curr_w, curr_h = cropped_img.size
        if curr_w < target_w or curr_h < target_h:
            filled_img = Image.new("RGBA", (target_w, target_h), (*MARKER_COLOR, 0))
            filled_img.paste(cropped_img, (0, 0))
            cropped_img = filled_img
            print(_("padded_image", w=target_w, h=target_h))

    if cropped_img.mode != 'RGBA':
        cropped_img = cropped_img.convert("RGBA")

    temp_input = os.path.join(temp_dir, "input_cropped.png")
    cropped_img.save(temp_input)

    # === Infer num_palettes from tilemap if used ===
    pal_indices = None
    if use_tilemap:
        if not os.path.exists(tilemap_path):
            raise FileNotFoundError(f"Tilemap not found: {tilemap_path}")
        with open(tilemap_path, 'rb') as f:
            data = f.read()
        if len(data) % 2 != 0:
            raise ValueError("Tilemap must have even length.")
        n_tiles = (cropped_img.size[0] // 8) * (cropped_img.size[1] // 8)
        if len(data) // 2 != n_tiles:
            raise ValueError("Tilemap length does not match number of tiles.")
        pal_indices = [(data[i] | (data[i+1] << 8)) >> 12 & 0xF for i in range(0, len(data), 2)]
        max_pal_idx = max(pal_indices) if pal_indices else 0
        num_palettes = max_pal_idx + 1

    print(_("splitting_groups"))
    groups_dir, pal_indices_out = split_into_groups(
        temp_input,
        tilemap_path,
        use_tilemap=use_tilemap,
        num_palettes=num_palettes
    )
    final_pal_indices = pal_indices if use_tilemap else pal_indices_out

    print(_("quantizing_irfanview"))
    indexed_dir = quantize_with_irfanview(groups_dir)

    print(_("applying_gba_palette"))
    apply_gba_palette_format(indexed_dir)

    print(_("extracting_palettes"))
    palettes = extract_palettes_from_indexed(indexed_dir, num_palettes=num_palettes)

    print(_("rebuilding_image"))
    reconstructed_path = os.path.join(temp_dir, "reconstructed.png")
    final_img = rebuild_final_image(temp_input, final_pal_indices, indexed_dir, palettes, reconstructed_path)

    print(_("generating_assets"))
    final_palette = generate_final_assets(
        final_img,
        final_pal_indices,
        palettes,
        start_index=start_index,
        extra_transparent_tiles=extra_transparent_tiles,
        tile_width=tile_width,
        transparent_color=transparent_color,
        keep_transparent=keep_transparent
    )

    generate_preview_image(reconstructed_path, groups_dir, transparent_color)

    # === 7. Clean temp files ===
    if not keep_temp:
        try:
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print(_("temp_files_removed"))
        except Exception as e:
            print(_("error_cleaning_temp", e=e))
    else:
        print(_("temp_files_preserved"))


def cli_main():
    """Entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description=_("help_description"),
        epilog=_("help_epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", help="Input image (PNG)")
    parser.add_argument("--num-palettes", type=int, default=None, help="Number of palettes to use (1-16). Cannot be used with --tilemap.)")
    parser.add_argument("--start-index", type=int, default=0, help="Starting palette index (0-15)")
    parser.add_argument("--transparent-color", type=str, default="0,0,0", help='Transparent color "R,G,B" (e.g. "192,200,164")')
    parser.add_argument("--tilemap", type=str, help="Tilemap .bin file with palette per tile (optional)")
    parser.add_argument("--extra-transparent-tiles", type=int, default=0, help="Extra transparent tiles to add at start (after ID 0)")
    parser.add_argument("--tileset-width", type=int, default=None, help="Tileset preview width in tiles (1-64, default: auto)")
    parser.add_argument("--origin", type=str, default="0,0", help='Crop origin: "10,20" or "1t,2t"')
    parser.add_argument("--end", type=str, help='Crop end: "64,64" or "8t,8t"')
    parser.add_argument("--output-size", type=str, help='Output size: "16,16" (px), "8t,8t", or preset: screen, bg0, bg1, bg2, bg3')
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files in temp/ folder")
    parser.add_argument("--keep-transparent", action="store_true", help="Keep the transparent color in palette (instead of black)")

    args = parser.parse_args()

    # === Cannot use --tilemap and --num-palettes together ===
    if args.tilemap is not None and args.num_palettes is not None:
        print(_("error_tilemap_num_palettes_forbidden"))
        sys.exit(1)

    # === Set default num_palettes only if not provided ===
    num_palettes_arg = args.num_palettes if args.num_palettes is not None else 1

    # === Validate transparent-color ===
    try:
        trans_rgb = tuple(map(int, args.transparent_color.split(',')))
        if len(trans_rgb) != 3 or not all(0 <= c <= 255 for c in trans_rgb):
            raise ValueError
    except:
        print(_("error_transparent_color"))
        sys.exit(1)

    # === Call main with resolved num_palettes ===
    main(
        input_path=args.input,
        tilemap_path=args.tilemap,
        start_index=args.start_index,
        num_palettes=num_palettes_arg,
        transparent_color=trans_rgb,
        extra_transparent_tiles=args.extra_transparent_tiles,
        tile_width=args.tileset_width,
        origin=args.origin,
        end=args.end,
        output_size=args.output_size,
        keep_temp=args.keep_temp,
        keep_transparent=args.keep_transparent
    )


if __name__ == "__main__":
    cli_main()