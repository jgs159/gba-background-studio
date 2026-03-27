# core/tile_utils.py
import os
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from core.config import MARKER_COLOR
from core.palette_utils import rgb_to_gba_rounded
from core.image_utils import extract_tiles_rgba
from utils.translator import Translator
translator = Translator()

def split_into_groups(input_path, num_palettes=1, pal_indices=None):
    img = Image.open(input_path)
    if img.mode != 'RGBA':
        img = img.convert("RGBA")
    w, h = img.size
    w = (w // 8) * 8
    h = (h // 8) * 8
    img = img.crop((0, 0, w, h))
    tiles = extract_tiles_rgba(img)
    n_tiles = len(tiles)
    
    if pal_indices is not None:
        if len(pal_indices) != n_tiles:
            raise ValueError(f"Number of palette indices ({len(pal_indices)}) doesn't match number of tiles ({n_tiles})")
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
    
    unique_pal_indices = sorted(set(pal_indices))
    output_dir="temp"
    os.makedirs(output_dir, exist_ok=True)
    width_in_tiles = w // 8
    
    tile_assigned = [False] * n_tiles
    
    for group_idx, pal_idx in enumerate(unique_pal_indices):
        group_img = Image.new("RGBA", (w, h), (*MARKER_COLOR, 255))
        modified = False
        
        for i, tile in enumerate(tiles):
            if not tile_assigned[i] and pal_indices[i] == pal_idx:
                ty = (i // width_in_tiles) * 8
                tx = (i % width_in_tiles) * 8
                group_img.paste(tile, (tx, ty))
                modified = True
                tile_assigned[i] = True
        
        if modified:
            path = os.path.join(output_dir, f"group_{group_idx}.png")
            group_img.save(path)
            print(f"✓ Group {group_idx} (palette {pal_idx}): {sum(1 for x in pal_indices if x == pal_idx)} tiles")
    
    unassigned_count = sum(1 for assigned in tile_assigned if not assigned)
    if unassigned_count > 0:
        for i in range(n_tiles):
            if not tile_assigned[i]:
                pal_indices[i] = 0
    
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
    
    unique_pal_indices = sorted(set(pal_indices))
    pal_idx_to_group_idx = {pal_idx: group_idx for group_idx, pal_idx in enumerate(unique_pal_indices)}
    indexed_tiles = {}

    for group_idx, pal_idx in enumerate(unique_pal_indices):
        group_path = os.path.join(indexed_dir, f"group_{group_idx}_indexed.png")
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
