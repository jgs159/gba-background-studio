# core/tile_optimizer.py
import numpy as np
from PIL import Image as PilImage


def _extract_tiles(tileset_img):
    """Return list of (8x8 np.uint8 array) for every tile in the tileset."""
    arr = np.array(tileset_img)
    w = tileset_img.width // 8
    h = tileset_img.height // 8
    tiles = []
    for ty in range(h):
        for tx in range(w):
            tiles.append(arr[ty*8:ty*8+8, tx*8:tx*8+8].copy())
    return tiles


def _build_tileset_img(tiles, cols, palette):
    """Rebuild a PIL indexed image from a list of 8x8 arrays."""
    rows = (len(tiles) + cols - 1) // cols
    img = PilImage.new('P', (cols * 8, rows * 8))
    img.putpalette(palette)
    arr = np.zeros((rows * 8, cols * 8), dtype=np.uint8)
    for i, tile in enumerate(tiles):
        tx = (i % cols) * 8
        ty = (i // cols) * 8
        arr[ty:ty+8, tx:tx+8] = tile
    img = PilImage.fromarray(arr, mode='P')
    img.putpalette(palette)
    return img


def _read_tilemap(tilemap_data, w, h, tilemap_index_fn):
    """Return list of (tile_id, h_flip, v_flip, pal_id) for every tile."""
    entries = []
    for ty in range(h):
        for tx in range(w):
            idx = tilemap_index_fn(tx, ty)
            if idx * 2 + 2 > len(tilemap_data):
                entries.append((0, 0, 0, 0))
                continue
            entry = tilemap_data[idx * 2] | (tilemap_data[idx * 2 + 1] << 8)
            entries.append((
                entry & 0x3FF,
                (entry >> 10) & 1,
                (entry >> 11) & 1,
                (entry >> 12) & 0xF,
            ))
    return entries


def _write_tilemap(entries, tilemap_w, tilemap_h, tilemap_index_fn):
    """Serialize list of (tile_id, h_flip, v_flip, pal_id) back to bytes."""
    size = tilemap_w * tilemap_h * 2
    data = bytearray(size)
    for i, (tile_id, hf, vf, pal) in enumerate(entries):
        tx = i % tilemap_w
        ty = i // tilemap_w
        idx = tilemap_index_fn(tx, ty)
        if idx * 2 + 2 > size:
            continue
        e = (tile_id & 0x3FF) | (hf << 10) | (vf << 11) | (pal << 12)
        data[idx * 2]     = e & 0xFF
        data[idx * 2 + 1] = (e >> 8) & 0xFF
    return bytes(data)


def optimize_tiles(tileset_img, tilemap_data, tilemap_w, tilemap_h, tilemap_index_fn):
    """
    Detect flip-duplicate tiles and reuse them with flip bits.
    Returns (new_tileset_img, new_tilemap_data, old_tile_count, new_tile_count).
    If tilemap_data is None, only rebuilds the tileset deduplicating tiles.
    """
    tiles = _extract_tiles(tileset_img)
    palette = tileset_img.getpalette()
    cols = tileset_img.width // 8

    if not tilemap_data:
        seen = {}
        new_tiles = []
        for t in tiles:
            candidates = [
                (t,                       0, 0),
                (np.fliplr(t),            1, 0),
                (np.flipud(t),            0, 1),
                (np.fliplr(np.flipud(t)), 1, 1),
            ]
            matched = any(ct.tobytes() in seen for ct, _, _ in candidates)
            if not matched:
                seen[t.tobytes()] = len(new_tiles)
                new_tiles.append(t)
        new_tileset = _build_tileset_img(new_tiles, cols, palette)
        return new_tileset, None, len(tiles), len(new_tiles)
    tiles = _extract_tiles(tileset_img)
    entries = _read_tilemap(tilemap_data, tilemap_w, tilemap_h, tilemap_index_fn)
    palette = tileset_img.getpalette()
    cols = tileset_img.width // 8

    seen = {}
    new_tiles = []

    if tiles:
        seen[tiles[0].tobytes()] = 0
        new_tiles.append(tiles[0])

    new_entries = []
    for tile_id, hf, vf, pal in entries:
        if tile_id >= len(tiles):
            new_entries.append((0, 0, 0, pal))
            continue

        t = tiles[tile_id].copy()
        if hf: t = np.fliplr(t)
        if vf: t = np.flipud(t)

        candidates = [
            (t,                    0, 0),
            (np.fliplr(t),         1, 0),
            (np.flipud(t),         0, 1),
            (np.fliplr(np.flipud(t)), 1, 1),
        ]
        matched = False
        for ct, ch, cv in candidates:
            key = ct.tobytes()
            if key in seen:
                new_entries.append((seen[key], ch, cv, pal))
                matched = True
                break
        if not matched:
            new_id = len(new_tiles)
            key = t.tobytes()
            seen[key] = new_id
            new_tiles.append(t)
            new_entries.append((new_id, 0, 0, pal))

    new_tileset = _build_tileset_img(new_tiles, cols, palette)
    new_tilemap  = _write_tilemap(new_entries, tilemap_w, tilemap_h, tilemap_index_fn)
    return new_tileset, new_tilemap, len(tiles), len(new_tiles)


def deoptimize_tiles(tileset_img, tilemap_data, tilemap_w, tilemap_h, tilemap_index_fn):
    """
    Expand every flipped tilemap reference into a new unique tile.
    Returns (new_tileset_img, new_tilemap_data, old_tile_count, new_tile_count).
    If tilemap_data is None, returns tileset unchanged.
    """
    tiles = _extract_tiles(tileset_img)
    palette = tileset_img.getpalette()
    cols = tileset_img.width // 8

    if not tilemap_data:
        return tileset_img, None, len(tiles), len(tiles)

    entries = _read_tilemap(tilemap_data, tilemap_w, tilemap_h, tilemap_index_fn)

    seen = {}
    new_tiles = []
    new_entries = []

    if tiles:
        seen[tiles[0].tobytes()] = 0
        new_tiles.append(tiles[0])

    for tile_id, hf, vf, pal in entries:
        if tile_id >= len(tiles):
            new_entries.append((0, 0, 0, pal))
            continue
        t = tiles[tile_id].copy()
        if hf: t = np.fliplr(t)
        if vf: t = np.flipud(t)
        key = t.tobytes()
        if key not in seen:
            seen[key] = len(new_tiles)
            new_tiles.append(t)
        new_entries.append((seen[key], 0, 0, pal))

    new_tileset = _build_tileset_img(new_tiles, cols, palette)
    new_tilemap  = _write_tilemap(new_entries, tilemap_w, tilemap_h, tilemap_index_fn)
    return new_tileset, new_tilemap, len(tiles), len(new_tiles)


def convert_text_to_rotation(tileset_img, tilemap_data, tilemap_w, tilemap_h, tilemap_index_fn):
    """
    Convert Text Mode tilemap (2 bytes/tile) to Rotation/Scaling (1 byte/tile).
    Deoptimizes flips, deduplicates tiles, enforces 256-tile limit.
    Returns (new_tileset_img, new_tilemap_bytes, old_unique, new_unique).
    """
    from core.final_assets import revert_gba_tilemap_reorganization

    if tilemap_w > 32:
        linear_data = revert_gba_tilemap_reorganization(
            tilemap_data, tilemap_w, tilemap_h, tilemap_w, tilemap_h
        )
        def linear_idx(tx, ty):
            return ty * tilemap_w + tx
        new_ts, new_tm, old_count, _ = deoptimize_tiles(
            tileset_img, linear_data, tilemap_w, tilemap_h, linear_idx
        )
    else:
        new_ts, new_tm, old_count, _ = deoptimize_tiles(
            tileset_img, tilemap_data, tilemap_w, tilemap_h, tilemap_index_fn
        )

    tiles = _extract_tiles(new_ts)
    palette = new_ts.getpalette()
    cols = new_ts.width // 8
    n = tilemap_w * tilemap_h

    seen = {}
    unique_tiles = []
    rot_map = []

    if tiles:
        seen[tiles[0].tobytes()] = 0
        unique_tiles.append(tiles[0])

    for i in range(n):
        entry = new_tm[i * 2] | (new_tm[i * 2 + 1] << 8)
        tile_id = entry & 0x3FF
        if tile_id >= len(tiles):
            rot_map.append(0)
            continue
        key = tiles[tile_id].tobytes()
        if key not in seen:
            seen[key] = len(unique_tiles)
            unique_tiles.append(tiles[tile_id])
        rot_map.append(seen[key])

    new_unique = len(unique_tiles)
    if new_unique > 256:
        return None, None, old_count, new_unique

    rot_tilemap = bytes([t & 0xFF for t in rot_map])
    new_tileset = _build_tileset_img(unique_tiles, cols, palette)
    return new_tileset, rot_tilemap, old_count, new_unique


def convert_rotation_to_text(tileset_img, tilemap_data, tilemap_w, tilemap_h):
    """
    Convert Rotation/Scaling tilemap (1 byte/tile) to Text Mode (2 bytes/tile).
    Runs optimize_tiles to reduce count using flips.
    For tilemaps wider than 32 tiles, reorganizes into GBA 32x32 screen blocks.
    Returns (new_tileset_img, new_tilemap_bytes, old_unique, new_unique).
    """
    from core.final_assets import reorganize_tilemap_for_gba_bg
    n = tilemap_w * tilemap_h
    old_unique = len(set(tilemap_data[:n]))

    linear_text = bytearray(n * 2)
    for i in range(n):
        tile_id = tilemap_data[i] if i < len(tilemap_data) else 0
        linear_text[i * 2]     = tile_id & 0xFF
        linear_text[i * 2 + 1] = 0x00
    linear_text = bytes(linear_text)

    def linear_idx(tx, ty):
        return ty * tilemap_w + tx

    new_ts, opt_text, _, new_unique = optimize_tiles(
        tileset_img, linear_text, tilemap_w, tilemap_h, linear_idx
    )

    if tilemap_w > 32:
        tile_list = []
        for i in range(n):
            entry = opt_text[i * 2] | (opt_text[i * 2 + 1] << 8)
            tile_list.append((
                entry & 0x3FF,
                (entry >> 10) & 1,
                (entry >> 11) & 1,
                (entry >> 12) & 0xF,
            ))
        reorganized = reorganize_tilemap_for_gba_bg(tile_list, tilemap_w * 8, tilemap_h * 8)
        final = bytearray()
        for tile_id, hf, vf, pal in reorganized:
            e = (tile_id & 0x3FF) | (hf << 10) | (vf << 11) | (pal << 12)
            final.extend(e.to_bytes(2, 'little'))
        new_tm = bytes(final)
    else:
        new_tm = opt_text

    return new_ts, new_tm, old_unique, new_unique
