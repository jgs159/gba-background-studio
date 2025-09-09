# core/palette_utils.py
import os
from PIL import Image
import numpy as np
from core.config import MARKER_COLOR
from utils.translator import Translator
translator = Translator()

def rgb_to_gba_rounded(color):
    r, g, b = color
    return (
        min((r + 4) // 8 * 8, 248),
        min((g + 4) // 8 * 8, 248),
        min((b + 4) // 8 * 8, 248)
    )

def calculate_relative_luminance(color):
    r, g, b = color
    return round(0.3 * r + 0.59 * g + 0.11 * b)

def generate_grayscale_palette():
    colors = []
    for i in range(256):
        level = int((i / 255) * 248) & 0b11111000
        colors.append((level, level, level))
    return colors

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

def apply_gba_palette_format(indexed_dir, num_palettes=16):
    """
    Converts palette of each image to GBA 15-bit format.
    """
    for i in range(num_palettes):
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
            print(translator.tr("error_apply_gba_palette", i=i, e=e))

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
