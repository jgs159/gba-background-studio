# core/config.py
# === Marker color in GBA format (248, 0, 248) → bright magenta ===
MARKER_COLOR = (248, 0, 248)  # GBA 15-bit

# === Language setting (3-letter code) ===
LANGUAGE = "eng"  # Options: eng, spa, brp, fra, deu, ita, por, ind, hin, rus, jpn, cmn

PRESET_SIZES = {
    "screen": (256, 160),
    "bg0": (256, 256),
    "bg1": (512, 256),
    "bg2": (256, 512),
    "bg3": (512, 512),
}
