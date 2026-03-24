# ui/dialogs/conversion_params.py
def get_conversion_parameters(
    image_path, output_size, is_8bpp, palettes, transparent_color,
    extra_transparent, tileset_width, origin, img_width_tiles, img_height_tiles,
    custom_width, custom_height, output_width_tiles, output_height_tiles,
    start_index, palette_size,
    save_preview, keep_temp, keep_transparent, external_tilemap=None,
    is_rotation_mode=False
): 
    if output_size == "Custom":
        w = custom_width
        h = custom_height
        output_size_str = f"{w}t,{h}t"
    elif output_size == "Original":
        w = img_width_tiles
        h = img_height_tiles
        output_size_str = f"{w}t,{h}t"
    else:
        w = output_width_tiles
        h = output_height_tiles
        output_size_str = f"{w}t,{h}t"

    trans_rgb = tuple(map(int, transparent_color.split(','))) if transparent_color.strip() else (0, 0, 0)

    if is_8bpp:
        if start_index < 0 or start_index > 255:
            raise ValueError("Start index must be between 0-255")
        
        if palette_size == 0:
            palette_size_val = 256 - start_index
        else:
            palette_size_val = palette_size
            if start_index + palette_size_val > 256:
                raise ValueError("Start index + palette size cannot exceed 256")

        return {
            'input_path': image_path,
            'tilemap_path': external_tilemap,
            'selected_palettes': None,
            'transparent_color': trans_rgb,
            'extra_transparent_tiles': extra_transparent,
            'tile_width': tileset_width if tileset_width > 0 else None,
            'origin': origin,
            'end': None,
            'output_size': output_size_str,
            'save_preview': save_preview,
            'keep_temp': keep_temp,
            'keep_transparent': keep_transparent,
            'bpp': 8,
            'start_index': start_index,
            'palette_size': palette_size_val,
            'rotation_mode': is_rotation_mode
        }
    else:
        if external_tilemap:
            selected_palettes = None
        else:
            selected_palettes = palettes if palettes else [0]
            if not all(0 <= p <= 15 for p in selected_palettes):
                raise ValueError("Palette indices must be between 0-15")

        return {
            'input_path': image_path,
            'tilemap_path': external_tilemap,
            'selected_palettes': selected_palettes,
            'transparent_color': trans_rgb,
            'extra_transparent_tiles': extra_transparent,
            'tile_width': tileset_width if tileset_width > 0 else None,
            'origin': origin,
            'end': None,
            'output_size': output_size_str,
            'save_preview': save_preview,
            'keep_temp': keep_temp,
            'keep_transparent': keep_transparent,
            'bpp': 4,
            'start_index': 0,
            'palette_size': 256,
            'rotation_mode': is_rotation_mode
        }
