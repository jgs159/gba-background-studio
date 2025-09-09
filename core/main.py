# core/main.py
import os
# === Suppress joblib warnings ===
os.environ['JOBLIB_WORKER_COUNT'] = '4'
os.environ['JOBLIB_MULTIPROCESSING'] = '0'
os.environ['LOKY_MAX_CPU_COUNT'] = '4'

import sys
import argparse
import shutil
import numpy as np
from PIL import Image
from core.config import PRESET_SIZES, MARKER_COLOR
from utils.translator import Translator
from core.final_assets import generate_final_assets_4bpp, generate_final_assets_8bpp
from core.tile_utils import split_into_groups, rebuild_final_image
from core.image_utils import create_gbagfx_preview_4bpp, create_gbagfx_preview_8bpp
from core.quantization import quantize_with_irfanview, quantize_to_n_colors_8bpp
from core.palette_utils import apply_gba_palette_format, extract_palettes_from_indexed
translator = Translator()

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

def parse_selected_palettes(value):
    """Parse selected palettes: '0,1,3,6,7,8' → [0,1,3,6,7,8]"""
    if not value:
        return [0]
    try:
        indices = [int(x.strip()) for x in value.split(",") if x.strip()]
        if not all(0 <= i <= 15 for i in indices):
            raise ValueError("Index out of range")
        return sorted(set(indices))
    except:
        return None

def clean_output(output_dir="output"):
    """Cleans the output directory, removing all files."""
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            print(translator.tr("output_cleaned"))
        except Exception as e:
            print(translator.tr("error_cleaning_output", e=e))
            sys.exit(1)
    os.makedirs(output_dir, exist_ok=True)

def apply_crop_and_resize(img, origin, end, output_size, img_w, img_h):
    orig_x, orig_y = origin
    if orig_x < 0 or orig_y < 0 or orig_x >= img_w or orig_y >= img_h:
        print(translator.tr("error_origin_out_of_bounds", x=orig_x, y=orig_y, w=img_w, h=img_h))
        return None
    cropped_img = None
    if end is not None:
        fin_x, fin_y = end
        crop_w = ((fin_x - orig_x) // 8) * 8
        crop_h = ((fin_y - orig_y) // 8) * 8
        if crop_w <= 0 or crop_h <= 0:
            print(translator.tr("error_crop_too_small"))
            return None
        end_x = orig_x + crop_w
        end_y = orig_y + crop_h
        cropped_img = img.crop((orig_x, orig_y, min(end_x, img_w), min(end_y, img_h)))
    elif output_size is not None:
        target_w, target_h = output_size
        end_x = orig_x + target_w
        end_y = orig_y + target_h
        if end_x > img_w or end_y > img_h:
            print(translator.tr("error_crop_exceeds", w=end_x, h=end_y, aw=img_w, ah=img_h))
            return None
        cropped_img = img.crop((orig_x, orig_y, end_x, end_y))
    else:
        if img_w > 1024 or img_h > 2048:
            print(translator.tr("error_image_too_big"))
            return None
        if img_w % 8 != 0 or img_h % 8 != 0:
            print(translator.tr("error_dimensions_not_multiple"))
            return None
        cropped_img = img.copy()
        print(translator.tr("image_valid", w=img_w, h=img_h))
    if output_size is not None:
        target_w, target_h = output_size
        curr_w, curr_h = cropped_img.size
        if curr_w < target_w or curr_h < target_h:
            filled_img = Image.new("RGBA", (target_w, target_h), (*MARKER_COLOR, 0))
            filled_img.paste(cropped_img, (0, 0))
            cropped_img = filled_img
            print(translator.tr("padded_image", w=target_w, h=target_h))
    if cropped_img.mode != 'RGBA':
        cropped_img = cropped_img.convert("RGBA")
    return cropped_img

def main(input_path, tilemap_path=None, selected_palettes=None, transparent_color=(0,0,0), extra_transparent_tiles=0, tile_width=None, origin=None, end=None, output_size=None, save_preview=False, keep_temp=False, keep_transparent=False, bpp=4, start_index=0, palette_size=256):
    use_tilemap = tilemap_path is not None
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Validate bpp
    if bpp not in (4, 8):
        print(translator.tr("error_bpp_invalid"))
        sys.exit(1)

    # Common variables
    reconstructed_path = None
    preview_source_dir = temp_dir

    # === PROCESS ACCORDING TO BPP ===
    if bpp == 4:
        # --- 4bpp Flow ---
        if selected_palettes is None:
            selected_palettes = [0]
        if not all(0 <= p <= 15 for p in selected_palettes):
            print(translator.tr("error_selected_palettes_invalid"))
            sys.exit(1)
        if len(selected_palettes) == 0:
            print(translator.tr("error_selected_palettes_empty"))
            sys.exit(1)

        try:
            img = Image.open(input_path)
            w, h = img.size
        except Exception as e:
            print(translator.tr("error_loading_image", e=e))
            sys.exit(1)

        origin_parsed = parse_pair(origin, w, h) if origin else (0, 0)
        end_parsed = parse_pair(end, w, h) if end else None
        output_size_parsed = parse_size(output_size)

        cropped_img = apply_crop_and_resize(img, origin_parsed, end_parsed, output_size_parsed, w, h)
        if cropped_img is None:
            return

        if cropped_img.mode != 'RGBA':
            cropped_img = cropped_img.convert("RGBA")

        arr = np.array(cropped_img)
        r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
        tc = transparent_color
        mask = (r == tc[0]) & (g == tc[1]) & (b == tc[2]) & (a > 128)
        count = np.sum(mask)
        if count > 0:
            arr[mask, 0] = MARKER_COLOR[0]
            arr[mask, 1] = MARKER_COLOR[1]
            arr[mask, 2] = MARKER_COLOR[2]
            arr[mask, 3] = 255
            cropped_img = Image.fromarray(arr)

        temp_input = os.path.join(temp_dir, "input_cropped.png")
        cropped_img.save(temp_input)

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
            unique_pal_indices = set(pal_indices) if pal_indices else set()
            selected_palettes = sorted(unique_pal_indices)
            num_palettes = len(selected_palettes)
        else:
            num_palettes = len(selected_palettes)

        print(translator.tr("splitting_groups"), flush=True)
        groups_dir, pal_indices_out = split_into_groups(
            temp_input,
            num_palettes=num_palettes,
            pal_indices=pal_indices if use_tilemap else None
        )
        final_pal_indices = pal_indices if use_tilemap else pal_indices_out

        print(translator.tr("quantizing_irfanview"), flush=True)
        indexed_dir = quantize_with_irfanview(
            groups_dir,
            selected_palettes=selected_palettes,
            transparent_color=transparent_color,
            keep_transparent=keep_transparent
        )

        print(translator.tr("extracting_palettes"), flush=True)
        palettes = extract_palettes_from_indexed(indexed_dir, num_palettes=num_palettes)

        print(translator.tr("rebuilding_image"), flush=True)
        reconstructed_path = os.path.join(temp_dir, "reconstructed.png")
        final_img = rebuild_final_image(temp_input, final_pal_indices, indexed_dir, palettes, reconstructed_path)

        print(translator.tr("generating_assets"), flush=True)
        clean_output()
        generate_final_assets_4bpp(
            final_img,
            final_pal_indices,
            selected_palettes=selected_palettes,
            extra_transparent_tiles=extra_transparent_tiles,
            tile_width=tile_width,
        )

    else:  # bpp == 8
        # --- 8bpp Flow ---
        print(translator.tr("status_processing_8bpp"), flush=True)

        if start_index < 0 or start_index > 255:
            print(translator.tr("error_start_index_8bpp"), flush=True)
            sys.exit(1)
        if palette_size < 1 or palette_size > 256:
            print(translator.tr("error_palette_size"), flush=True)
            sys.exit(1)
        if start_index + palette_size > 256:
            print(translator.tr("error_palette_overflow"), flush=True)
            sys.exit(1)

        try:
            img = Image.open(input_path)
            w, h = img.size
        except Exception as e:
            print(translator.tr("error_loading_image", e=e), flush=True)
            sys.exit(1)

        origin_parsed = parse_pair(origin, w, h) if origin else (0, 0)
        end_parsed = parse_pair(end, w, h) if end else None
        output_size_parsed = parse_size(output_size)

        cropped_img = apply_crop_and_resize(img, origin_parsed, end_parsed, output_size_parsed, w, h)
        if cropped_img is None:
            sys.exit(1)

        temp_input = os.path.join(temp_dir, "input_cropped.png")
        cropped_img.save(temp_input)
        print(translator.tr("image_saved_cropped"), flush=True)

        print(translator.tr("splitting_groups"), flush=True)

        arr = np.array(cropped_img)
        r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
        tc = transparent_color
        mask = (r == tc[0]) & (g == tc[1]) & (b == tc[2]) & (a > 128)
        count = np.sum(mask)
        if count > 0:
            arr[mask, 0] = MARKER_COLOR[0]
            arr[mask, 1] = MARKER_COLOR[1]
            arr[mask, 2] = MARKER_COLOR[2]
            arr[mask, 3] = 255
            cropped_img = Image.fromarray(arr)
        marker_img = cropped_img

        marker_path = os.path.join(temp_dir, "01_marker.png")
        marker_img.save(marker_path)

        print(translator.tr("quantizing_internal"), flush=True)
        try:
            quantized_img, palette_colors = quantize_to_n_colors_8bpp(
                marker_img,
                palette_size,
                start_index=start_index,
                transparent_color=transparent_color,
                keep_transparent=keep_transparent
            )
        except Exception as e:
            print(translator.tr("error_quantizing", e=e), flush=True)
            sys.exit(1)

        quantized_path = os.path.join(temp_dir, "02_quantized.png")
        quantized_img.save(quantized_path)

        reconstructed_path = os.path.join(temp_dir, "reconstructed.png")
        quantized_img.save(reconstructed_path)

        clean_output()
        generate_final_assets_8bpp(
            quantized_img,
            start_index=start_index,
            palette_size=palette_size,
            extra_transparent_tiles=extra_transparent_tiles,
            tile_width=tile_width,
        )

    os.makedirs("temp/preview", exist_ok=True)
    if bpp == 4:
        create_gbagfx_preview_4bpp(selected_palettes=selected_palettes, save_preview=save_preview, transparent_color=transparent_color, keep_transparent=keep_transparent)
    else:  # bpp == 8
        create_gbagfx_preview_8bpp(save_preview=save_preview, transparent_color=transparent_color, keep_transparent=keep_transparent)
    print(translator.tr("preview_generated", path="temp/preview/preview.png"), flush=True)

    # === 2. Clean temp/ (common) ===
    if not keep_temp:
        try:
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if item == "preview":
                    continue
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print(translator.tr("temp_files_removed"), flush=True)
        except Exception as e:
            print(translator.tr("error_cleaning_temp", e=e), flush=True)
    else:
        print(translator.tr("temp_files_preserved"), flush=True)

def cli_main():
    parser = argparse.ArgumentParser(
        description=translator.tr("help_description"),
        epilog=translator.tr("help_epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", help="Input image (PNG)")
    parser.add_argument("--selected-palettes", type=str, default="0", help='Comma-separated list of palette indices to use: "0,1,3,6,7,8" (only for 4bpp)')
    parser.add_argument("--transparent-color", type=str, default="0,0,0", help='Transparent color "R,G,B" (e.g. "192,200,164")')
    parser.add_argument("--tilemap", type=str, help="Tilemap .bin file with palette per tile (optional)")
    parser.add_argument("--extra-transparent-tiles", type=int, default=0, help="Extra transparent tiles to add at start (after ID 0)")
    parser.add_argument("--tileset-width", type=int, default=None, help="Tileset preview width in tiles (1-64, default: auto)")
    parser.add_argument("--origin", type=str, default="0,0", help='Crop origin: "10,20" or "1t,2t"')
    parser.add_argument("--end", type=str, help='Crop end: "64,64" or "8t,8t"')
    parser.add_argument("--output-size", type=str, help='Output size: "16,16" (px), "8t,8t", or preset: screen, bg0, bg1, bg2, bg3')
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files in temp/ folder")
    parser.add_argument("--keep-transparent", action="store_true", help="Keep the transparent color in palette (instead of black)")
    parser.add_argument("--save-preview", action="store_true", help="Keep preview files in the output folder")
    parser.add_argument("--bpp", type=int, choices=[4, 8], default=4, help="Bits per pixel: 4 (16 colors) or 8 (256 colors)")
    parser.add_argument("--start-index", type=int, default=0, help="Starting color index in palette (0-255, only for 8bpp)")
    parser.add_argument("--palette-size", type=int, default=None, help="Number of colors in palette (1-256). Default: 256 - start-index (only for 8bpp)")

    args = parser.parse_args()

    # Parse selected_palettes
    selected_palettes = parse_selected_palettes(args.selected_palettes)
    if selected_palettes is None:
        print(translator.tr("error_selected_palettes_invalid"))
        sys.exit(1)

    # Validate transparent-color
    try:
        trans_rgb = tuple(map(int, args.transparent_color.split(',')))
        if len(trans_rgb) != 3 or not all(0 <= c <= 255 for c in trans_rgb):
            raise ValueError
    except:
        print(translator.tr("error_transparent_color"))
        sys.exit(1)

    # === Handling start_index and palette_size (only for bpp=8) ===
    start_index = args.start_index
    palette_size = args.palette_size

    if args.bpp == 8:
        if start_index < 0 or start_index > 255:
            print(translator.tr("error_start_index_8bpp"))
            sys.exit(1)
        if palette_size is None:
            palette_size = 256 - start_index
        else:
            if palette_size < 1 or palette_size > 256:
                print(translator.tr("error_palette_size"))
                sys.exit(1)
        if start_index + palette_size > 256:
            print(translator.tr("error_palette_overflow"))
            sys.exit(1)
    else:
        start_index = 0
        palette_size = 256

    # === Call main ===
    main(
        input_path=args.input,
        tilemap_path=args.tilemap,
        selected_palettes=selected_palettes,
        transparent_color=trans_rgb,
        extra_transparent_tiles=args.extra_transparent_tiles,
        tile_width=args.tileset_width,
        origin=args.origin,
        end=args.end,
        output_size=args.output_size,
        save_preview=args.save_preview,
        keep_temp=args.keep_temp,
        keep_transparent=args.keep_transparent,
        bpp=args.bpp,
        start_index=start_index,
        palette_size=palette_size
    )

if __name__ == "__main__":
    cli_main()
