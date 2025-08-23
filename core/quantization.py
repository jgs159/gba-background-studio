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
from core.language import translate

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

    raise FileNotFoundError(f"No se encontró IrfanView. Por favor instala la versión {'64' if is_64bit else '32'}-bit desde irfanview.info")

def quantize_with_irfanview(groups_dir, irfanview_path=None, selected_palettes=None, transparent_color=(0,0,0), keep_transparent=False):
    indexed_dir = os.path.join(groups_dir, "01_indexed")
    reindexed_dir = os.path.join(groups_dir, "02_reindexed")
    os.makedirs(indexed_dir, exist_ok=True)
    os.makedirs(reindexed_dir, exist_ok=True)
    if irfanview_path is None:
        irfanview_path = get_irfanview_path()

    # Pre-calcular valores
    transparent_color_gba = rgb_to_gba_rounded(transparent_color)
    final_color_0 = transparent_color_gba if keep_transparent else (0, 0, 0)
    marker_gba = rgb_to_gba_rounded(MARKER_COLOR)

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

            # === 1. Reordenar por luminancia (índice 0 se maneja después) ===
            work = rgb_palette[1:]  # Excluir índice 0
            indexed_colors = [(idx, color) for idx, color in enumerate(work)]
            indexed_colors.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))

            reordered_rgb = [rgb_palette[0]]  # Índice 0 temporal
            for old_idx, color in indexed_colors:
                reordered_rgb.append(color)

            # === 2. Ajustar índice 0 según MARKER_COLOR y keep_transparent ===
            print(translate("applying_gba_palette"), flush=True)
            gba_palette = [rgb_to_gba_rounded(c) for c in reordered_rgb]
            marker_indices = [j for j, c in enumerate(gba_palette) if c == marker_gba]

            if marker_indices:
                # Si hay MARKER_COLOR, moverlo al índice 0
                marker_idx = marker_indices[0]
                if marker_idx != 0:
                    reordered_rgb[0] = MARKER_COLOR
                    reordered_rgb[marker_idx] = rgb_palette[0]  # intercambiar
                else:
                    reordered_rgb[0] = MARKER_COLOR
            else:
                # Si no hay MARKER_COLOR, insertar en índice 0
                reordered_rgb[0] = MARKER_COLOR

            # === 3. Aplicar keep_transparent: índice 0 = transparent_color o negro ===
            if keep_transparent:
                reordered_rgb[0] = transparent_color_gba
            else:
                reordered_rgb[0] = (0, 0, 0)

            # === 4. Reindexar imagen según nueva paleta ===
            img_data = np.array(img)
            new_img = Image.new("P", img.size)

            flat_palette = []
            for color in reordered_rgb:
                flat_palette.extend(color)
            while len(flat_palette) < 768:
                flat_palette.append(0)
            new_img.putpalette(flat_palette)

            # Mapear índices antiguos a nuevos
            old_to_new = {}
            for new_idx, color in enumerate(reordered_rgb):
                # Buscar el índice original más cercano
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

            # Aplicar mapeo
            img_flat = img_data.flatten()
            new_flat = np.array([old_to_new.get(idx, 0) for idx in img_flat])
            new_img.putdata(new_flat.tolist())

            output_2 = os.path.abspath(os.path.join(reindexed_dir, f"group_{i}_indexed.png"))
            new_img.save(output_2)

        except Exception as e:
            print(translate("error_ensure_gba", e=e))
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
        raise ValueError(translate("error_no_valid_pixels"))

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

    # === 1. Extraer subpaleta reducida (en RGB, sin GBA) ===
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

    # === 2. Reordenar por luminancia (en RGB) ===
    print(translate("applying_gba_palette"), flush=True)
    transparent_color_gba = rgb_to_gba_rounded(transparent_color)
    final_color_0 = transparent_color_gba if keep_transparent else (0, 0, 0)

    if start_index == 0:
        # Índice 0 = transparente, el resto se reordenan
        indexed_colors = [(i, color) for i, color in enumerate(reduced_palette)]
        indexed_colors.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))
        reordered_palette = [final_color_0]  # Índice 0
        reordered_palette.extend((r, g, b) for _, (r, g, b) in indexed_colors)  # En RGB
    else:
        indexed_colors = [(i, color) for i, color in enumerate(reduced_palette)]
        indexed_colors.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))
        reordered_palette = [(r, g, b) for _, (r, g, b) in indexed_colors]  # En RGB

    # === 3. Mapear píxeles a índices usando distancia en RGB ===
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

            # Calcular distancias euclidianas al cuadrado
            distances = np.sum((palette_rgb - [r, g, b])**2, axis=1)
            closest_idx = np.argmin(distances)

            if start_index == 0:
                indices[y, x] = closest_idx + 1
            else:
                indices[y, x] = start_index + closest_idx

    # === 4. Construir paleta completa de 256 colores convertida a GBA ===
    full_palette_gba = [(255, 255, 255)] * 256  # blanco = vacío

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

    # === 5. Crear imagen paletizada ===
    print(translate("rebuilding_image"), flush=True)
    out_img = Image.fromarray(indices, mode="P")

    # Paleta final: reemplazar blancos por negro
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
