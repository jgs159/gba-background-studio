# core/config.py
# === Marker color in GBA format (248, 0, 248) → bright magenta ===
MARKER_COLOR = (248, 0, 248)  # GBA 15-bit

# === Valid GBA Rotation/Scaling mode tilemap sizes (in tiles) ===
ROT_SIZES = [(16, 16), (32, 32), (64, 64), (128, 128)]
ROT_SIZES_SET = {(16, 16), (32, 32), (64, 64), (128, 128)}

# === Language setting (3-letter code) ===
LANGUAGE = "eng"  # Options: eng, spa, brp, fra, deu, ita, por, ind, hin, rus, jpn, cmn

PRESET_SIZES = {
    "screen": (256, 160),
    "bg0": (256, 256),
    "bg1": (512, 256),
    "bg2": (256, 512),
    "bg3": (512, 512),
}

def validate_gba_dimensions(width_tiles, height_tiles):
    if width_tiles == 64 and height_tiles == 32:
        return False, width_tiles, height_tiles, "Screen Size 1"
    if width_tiles == 32 and height_tiles == 64:
        return False, width_tiles, height_tiles, "Screen Size 2"
    if width_tiles == 64 and height_tiles == 64:
        return False, width_tiles, height_tiles, "Screen Size 3"
    if width_tiles == 32 and height_tiles == 32:
        return False, width_tiles, height_tiles, "Screen Size 0"
    
    adjusted_w = ((width_tiles + 31) // 32) * 32
    adjusted_h = ((height_tiles + 31) // 32) * 32
    
    needs_adjustment = (adjusted_w != width_tiles) or (adjusted_h != height_tiles)
    
    if needs_adjustment:
        if adjusted_w == 64 and adjusted_h == 32:
            bg_type = "Screen Size 1"
        elif adjusted_w == 32 and adjusted_h == 64:
            bg_type = "Screen Size 2"
        elif adjusted_w == 64 and adjusted_h == 64:
            bg_type = "Screen Size 3"
        else:
            bg_type = "Custom"
        
        return True, adjusted_w, adjusted_h, bg_type
    
    return False, width_tiles, height_tiles, "Compatible"
