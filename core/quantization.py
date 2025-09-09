# core/quantization.py
import os
import sys
import platform
import subprocess
import shutil
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from core.palette_utils import rgb_to_gba_rounded, calculate_relative_luminance
from core.config import MARKER_COLOR
from utils.translator import Translator
translator = Translator()

def get_irfanview_path():
    if sys.platform != "win32":
        return "wine ~/.wine/drive_c/Program Files/IrfanView/i_view64.exe"

    is_64bit = platform.machine().endswith('64')
    
    if is_64bit:
        paths = [
            os.path.expandvars("%ProgramFiles%\\IrfanView\\i_view64.exe"),
            "C:\\Program Files\\IrfanView\\i_view64.exe"
        ]
    else:
        paths = [
            os.path.expandvars("%ProgramFiles%\\IrfanView\\i_view32.exe"),
            "C:\\Program Files\\IrfanView\\i_view32.exe"
        ]
    
    paths.extend([
        os.path.expandvars("%ProgramFiles(x86)%\\IrfanView\\i_view32.exe"),
        "C:\\Program Files (x86)\\IrfanView\\i_view32.exe"
    ])

    for path in paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(f"IrfanView not found. Please install the {'64' if is_64bit else '32'}-bit version from irfanview.info")

def quantize_with_irfanview(groups_dir, irfanview_path=None, selected_palettes=None, transparent_color=(0,0,0), keep_transparent=False):
    indexed_dir = os.path.join(groups_dir, "01_indexed")
    reindexed_dir = os.path.join(groups_dir, "02_reindexed")
    os.makedirs(indexed_dir, exist_ok=True)
    os.makedirs(reindexed_dir, exist_ok=True)
    if irfanview_path is None:
        irfanview_path = get_irfanview_path()

    # Pre-calculate values
    transparent_color_gba = rgb_to_gba_rounded(transparent_color)
    final_color_0 = transparent_color_gba if keep_transparent else (0, 0, 0)
    marker_gba = rgb_to_gba_rounded(MARKER_COLOR)

    print(translator.tr("applying_gba_palette"), flush=True)
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

        try:
            img = Image.open(output_1)
            if img.mode != 'P':
                shutil.copy2(output_1, os.path.join(reindexed_dir, f"group_{i}_indexed.png"))
                continue

            palette = img.getpalette()
            rgb_palette = []
            for j in range(16):
                r = palette[j*3]
                g = palette[j*3+1]
                b = palette[j*3+2]
                rgb_palette.append((r, g, b))

            work = rgb_palette[1:]
            indexed_colors = [(idx, color) for idx, color in enumerate(work)]
            indexed_colors.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))

            reordered_rgb = [rgb_palette[0]]
            for old_idx, color in indexed_colors:
                reordered_rgb.append(color)

            gba_palette = [rgb_to_gba_rounded(c) for c in reordered_rgb]
            marker_indices = [j for j, c in enumerate(gba_palette) if c == marker_gba]

            if marker_indices:
                marker_idx = marker_indices[0]
                if marker_idx != 0:
                    reordered_rgb[0] = MARKER_COLOR
                    reordered_rgb[marker_idx] = rgb_palette[0]
                else:
                    reordered_rgb[0] = MARKER_COLOR
            else:
                reordered_rgb[0] = MARKER_COLOR

            if keep_transparent:
                reordered_rgb[0] = transparent_color_gba
            else:
                reordered_rgb[0] = (0, 0, 0)

            img_data = np.array(img)
            new_img = Image.new("P", img.size)

            flat_palette = []
            for color in reordered_rgb:
                flat_palette.extend(color)
            while len(flat_palette) < 768:
                flat_palette.append(0)
            new_img.putpalette(flat_palette)

            old_to_new = {}
            for new_idx, color in enumerate(reordered_rgb):
                best_old_idx = 0
                best_dist = float('inf')
                for old_idx in range(16):
                    dr = rgb_palette[old_idx][0] - color[0]
                    dg = rgb_palette[old_idx][1] - color[1]
                    db = rgb_palette[old_idx][2] - color[2]
                    dist = dr*dr + dg*dg + db*db
                    if dist < best_dist:
                        best_dist = dist
                        best_old_idx = old_idx
                old_to_new[best_old_idx] = new_idx

            img_flat = img_data.flatten()
            new_flat = np.array([old_to_new.get(idx, 0) for idx in img_flat])
            new_img.putdata(new_flat.tolist())

            output_2 = os.path.abspath(os.path.join(reindexed_dir, f"group_{i}_indexed.png"))
            new_img.save(output_2)

        except Exception as e:
            print(translator.tr("error_ensure_gba", e=e))
            shutil.copy2(output_1, os.path.join(reindexed_dir, f"group_{i}_indexed.png"))

    return reindexed_dir

def quantize_to_n_colors_8bpp(img, n_colors, start_index=0, transparent_color=(0, 0, 0), keep_transparent=False):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    h, w, _ = arr.shape

    alpha = arr[:, :, 3]
    opaque = alpha > 128
    pixels = arr[opaque][:, :3]

    if len(pixels) == 0:
        raise ValueError(translator.tr("error_no_valid_pixels"))

    mask_marker = (arr[:, :, 0] == MARKER_COLOR[0]) & \
                  (arr[:, :, 1] == MARKER_COLOR[1]) & \
                  (arr[:, :, 2] == MARKER_COLOR[2]) & \
                  (opaque)
    has_marker = np.any(mask_marker)

    cluster_pixels = pixels.copy()
    if has_marker:
        not_marker = ~((pixels[:, 0] == MARKER_COLOR[0]) & 
                       (pixels[:, 1] == MARKER_COLOR[1]) & 
                       (pixels[:, 2] == MARKER_COLOR[2]))
        cluster_pixels = pixels[not_marker]

    if start_index == 0:
        n_clusters = min(n_colors - 1, len(cluster_pixels)) if n_colors > 1 else 1
    else:
        n_clusters = min(n_colors, len(cluster_pixels))

    if n_clusters <= 0:
        n_clusters = 1

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(cluster_pixels)
    cluster_centers = kmeans.cluster_centers_.round(0).astype(int)

    reduced_palette = []
    if start_index == 0:
        for i in range(n_colors - 1):
            if i < len(cluster_centers):
                r, g, b = cluster_centers[i]
                reduced_palette.append((int(r), int(g), int(b)))
            else:
                reduced_palette.append((0, 0, 0))
    else:
        for i in range(n_colors):
            if i < len(cluster_centers):
                r, g, b = cluster_centers[i]
                reduced_palette.append((int(r), int(g), int(b)))
            else:
                reduced_palette.append((0, 0, 0))

    print(translator.tr("applying_gba_palette"), flush=True)
    transparent_color_gba = rgb_to_gba_rounded(transparent_color)
    final_color_0 = transparent_color_gba if keep_transparent else (0, 0, 0)

    if start_index == 0:
        indexed_colors = [(i, color) for i, color in enumerate(reduced_palette)]
        indexed_colors.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))
        reordered_palette = [final_color_0]  # Índice 0
        reordered_palette.extend((r, g, b) for _, (r, g, b) in indexed_colors)
    else:
        indexed_colors = [(i, color) for i, color in enumerate(reduced_palette)]
        indexed_colors.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))
        reordered_palette = [(r, g, b) for _, (r, g, b) in indexed_colors]

    palette_rgb_list = reordered_palette[1:] if start_index == 0 else reordered_palette

    if not palette_rgb_list:
        palette_rgb = np.array([[0, 0, 0]], dtype=int)
    else:
        palette_rgb = np.array(palette_rgb_list, dtype=int)

    indices = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            r, g, b, a = arr[y, x]
            if a <= 128 or (r, g, b) == MARKER_COLOR:
                indices[y, x] = 0
                continue

            distances = np.sum((palette_rgb - [r, g, b])**2, axis=1)
            closest_idx = np.argmin(distances)

            if start_index == 0:
                indices[y, x] = closest_idx + 1
            else:
                indices[y, x] = start_index + closest_idx

    full_palette_gba = [(255, 255, 255)] * 256 

    full_palette_gba[0] = final_color_0
    if start_index == 0:
        for i, (r, g, b) in enumerate(reordered_palette[1:], start=1):
            if i < 256:
                full_palette_gba[i] = rgb_to_gba_rounded((r, g, b))
    else:
        for i, (r, g, b) in enumerate(reordered_palette):
            idx = start_index + i
            if idx < 256:
                full_palette_gba[idx] = rgb_to_gba_rounded((r, g, b))

    print(translator.tr("rebuilding_image"), flush=True)
    out_img = Image.fromarray(indices, mode="P")

    final_palette = []
    for color in full_palette_gba:
        if color == (255, 255, 255):
            final_palette.append((0, 0, 0))
        else:
            final_palette.append(color)
            
    flat_palette = [c for color in final_palette for c in color]
    while len(flat_palette) < 768:
        flat_palette.append(0)
    out_img.putpalette(flat_palette)

    return out_img, final_palette
