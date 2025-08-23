# core/tile_utils.py
import os
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from core.config import MARKER_COLOR
from core.palette_utils import rgb_to_gba_rounded
from core.image_utils import extract_tiles_rgba
from core.language import translate


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

def group_consecutive_palettes(indices):
    """Group consecutive indices: [0,1,3,6,7,8] → [(0,2), (3,1), (6,3)]"""
    if not indices:
        return []
    indices = sorted(indices)
    groups = []
    start = indices[0]
    count = 1
    for i in range(1, len(indices)):
        if indices[i] == indices[i-1] + 1:
            count += 1
        else:
            groups.append((start, count))
            start = indices[i]
            count = 1
    groups.append((start, count))
    return groups
