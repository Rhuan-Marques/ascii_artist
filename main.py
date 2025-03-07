from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import cv2
import os
import time
from pydantic import BaseModel
import argparse
import sys
import datetime

# A set of ASCII characters ordered by “density” (from low to high)
ASCII_CHARS = [".", ",", ":", ";", "+", "*", "?", "%", "S", "#", "@"]

def choose_char(pixel, modifier: int = 0, inverse: bool = False):
    chars = ASCII_CHARS
    if inverse:
        chars = chars[::-1]
    adjusted_pixel = pixel + modifier
    adjusted_pixel = max(0, min(adjusted_pixel, 255))
    return chars[adjusted_pixel // 25]

def resize_image(image, new_width=100):
    """Resize image preserving aspect ratio."""
    width, height = image.size
    ratio = height / (width * 2)
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

def grayify(image):
    """Convert the image to grayscale."""
    return image.convert("L")

def increase_contrast(image, factor=1.5):
    """Increase the contrast of the image."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def increase_brightness(image, factor=1.5):
    """Increase the brightness of the image."""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def pixels_to_ascii(image, pixel_density: int = 1, inverse: bool = False):
    """Map each pixel to an ASCII char based on its intensity.
    (Works on grayscale images.)"""
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += choose_char(pixel, pixel_density, inverse)
    return ascii_str

def pixels_to_ascii_color(image, pixel_density: int = 1, inverse: bool = False):
    """
    Convert an RGB image to colored ASCII art.
    For each pixel, we compute its brightness using the luminosity formula,
    choose an ASCII character accordingly, then wrap it in ANSI escape codes
    to print with the original pixel's color.
    """
    width, height = image.size
    ascii_art_lines = []
    for y in range(height):
        line = ""
        r, g, b = (-9999, -9999, -9999)
        for x in range(width):
            nr, ng, nb = image.getpixel((x, y))
            # Compute brightness using the luminosity method
            brightness = int(0.299 * nr + 0.587 * ng + 0.114 * nb)
            char = choose_char(brightness, pixel_density, inverse)
            # Wrap the character in ANSI escape sequence for truecolor (24-bit)
            if nr != r or ng != g or nb != b:
                line += f"\033[38;2;{nr};{ng};{nb}m"
                r=nr
                g=ng
                b=nb
            line += f"{char}"
        ascii_art_lines.append(line+f'\033[0m')
    return "\n".join(ascii_art_lines) 

def add_text(image, top, bottom, font_path=None, margin=10):
    """
    Add the given text to the top and bottom of the image.
    The font size is dynamically determined so that the text spans nearly the full width of the image.
    """
    if not top and not bottom:
        return image

    if image.mode != "RGB":
        image = image.convert("RGB")
    
    new_width = image.width
    target_width = new_width - 2 * margin

    if font_path is None and os.name != 'nt':
        font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttf"
    elif not font_path:
        font_path = "C:/Windows/Fonts/arialbd"

    font_size = 10
    top_end = None
    bottom_end = None

    while True:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f'Received font not found or default font not in default location: {e}')
            raise Exception(f'Received font not found or default font not in default location: {e}')
        
        dummy_img = Image.new("RGB", (new_width, 100))
        draw = ImageDraw.Draw(dummy_img)
        if top and not top_end:
            tbox = draw.textbbox((0, 0), top, font=font)
            text_width = tbox[2] - tbox[0]
            if text_width > target_width:
                top_end = font_size - 1
        if bottom and not bottom_end:
            bbox = draw.textbbox((0, 0), bottom, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width > target_width:
                bottom_end = font_size - 1
        if (top_end or not top) and (bottom_end or not bottom):
            break
        font_size += 1

    top_height = tbox[3] - tbox[1] + margin if top else 0
    bottom_height = bbox[3] - bbox[1] + margin if bottom else 0

    new_height = image.height + top_height + bottom_height
    new_width = image.width
    
    new_image = Image.new("RGB", (new_width, new_height), color="black")
    new_image.paste(image, (0, top_height))
    draw = ImageDraw.Draw(new_image)

    if top:
        top_font = ImageFont.truetype(font_path, top_end)
        text_x = 10
        text_y = margin 
        draw.text((text_x, text_y - (top_height // 3)), top, fill="white", font=top_font)
    if bottom:
        font = ImageFont.truetype(font_path, bottom_end)
        text_x = 10
        text_y = image.height + top_height + (margin // 2)
        draw.text((text_x, text_y - (bottom_height // 3)), bottom, fill="white", font=font)
    return new_image

def convert_image_to_ascii(image_path, new_width=100, contrast_factor=1.0, pixel_density: int = 1,
                           inverse: bool = False, text_above="", text_below="", color: bool = False):
    """Convert an image file to ASCII art, optionally adding text.
    If color mode is active, output is colored based on the original image."""
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Unable to open image file {image_path}.\nError: {e}")
        return

    image = add_text(image, text_above, text_below)
    temp_image_path = "temp.png"
    image.save(temp_image_path)
    image = resize_image(image, new_width)
    
    if contrast_factor != 1.0:
        image = increase_contrast(image, contrast_factor)
    
    if color:
        # Use the RGB image directly for color mode.
        ascii_image = pixels_to_ascii_color(image, pixel_density, inverse)
    else:
        image = grayify(image)
        ascii_str = pixels_to_ascii(image, pixel_density, inverse)
        img_width = image.width
        ascii_image = "\n".join(ascii_str[i:i+img_width] for i in range(0, len(ascii_str), img_width))
    
    return ascii_image

def video_to_frames(video_path, skip_frames=5):
    frames = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    frame_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_index % (skip_frames + 1) == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            frames.append(pil_image)
        
        frame_index += 1
    cap.release()
    return frames

class VideoConfig(BaseModel):
    skip_frames: int = 0
    repeat: int = 1
    time_bewtween_frames: float = 0.15

def print_as_ascii(
        image_path: str,
        new_width: int,
        contrast_factor: float,
        brightness_factor: float,
        pixel_density: int,
        inverse: bool,
        text_above: str,
        text_below: str,
        config: VideoConfig,
        color: bool,
        font_path: str,
        text_margin: int,
    ):
    """Convert an image or video file to ASCII art and print it.
    If color is True, prints colored ASCII art based on original image colors."""
    benchmark = ""
    if any(image_path.endswith(extension) for extension in [".mp4", ".avi", ".gif"]):
        frames = video_to_frames(image_path, config.skip_frames)
    else:
        try:
            frames = [Image.open(image_path)]
        except Exception as e:
            print(f"Unable to open image file {image_path}.\nError: {e}")
            return

    results = []
    add_txt = datetime.timedelta(0)
    pixels2ascii = datetime.timedelta(0)

    for frame in frames:
        before = datetime.datetime.now()
        image = add_text(frame, text_above, text_below, font_path=font_path, margin=text_margin)
        add_txt += datetime.datetime.now() - before
        image = resize_image(image, new_width)
        if contrast_factor != 1.0:
            image = increase_contrast(image, contrast_factor)
        
        if brightness_factor != 1.0:
            image = increase_brightness(image, brightness_factor)
        
        if color:
            before = datetime.datetime.now()
            ascii_image = pixels_to_ascii_color(image, pixel_density, inverse)
            pixels2ascii += datetime.datetime.now() - before
        else:
            image = grayify(image)
            ascii_str = pixels_to_ascii(image, pixel_density, inverse)
            img_width = image.width
            ascii_image = "\n".join(ascii_str[i:i+img_width] for i in range(0, len(ascii_str), img_width))
        
        results.append(ascii_image)
    
    if not results:
        raise ValueError("No frames found in the video.")

    benchmark += f"""
    AddText: {add_txt}
    P2A: {pixels2ascii}
    """
    
    if len(results) == 1:
        print(results[0])
        return
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    for _ in range(999999999 if config and config.repeat == -1 else config.repeat):
        for i, ascii_image in enumerate(results):
            sys.stdout.write(f'Frame {i+1}/{len(results)}\n{ascii_image}')
            sys.stdout.flush()
            time.sleep(config.time_bewtween_frames)
            sys.stdout.write("\033[999F")
        if config.repeat != -1:
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="The path to the file to be shown")
    parser.add_argument("--width", type=int, default=100, help="Width of the generated ASCII image (defaults to 100 chars)")
    parser.add_argument("--contrast", type=float, default=1.0, help="Contrast factor for the image (defaults to 1.0)")
    parser.add_argument("--brightness", type=float, default=1.0, help="Brightness factor for the image (defaults to 1.0)")
    parser.add_argument("--pixel_density", type=int, default=1, help="Pixel density for ASCII conversion (defaults to 1)")
    parser.add_argument("--text_above", type=str, default="", help="Text to add above the image.")
    parser.add_argument("--text_below", type=str, default="", help="Text to add below the image.")
    parser.add_argument("--skip_frames", type=int, default=0, help="Number of frames to skip in video files (defaults to 0)")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to repeat the video (-1 for infinite, defaults to 1)")
    parser.add_argument("--time_between_frames", type=float, default=0.15, help="Time between video frames in seconds (defaults to 0.15)")
    parser.add_argument("--color", action="store_true", help="Print colored ASCII art based on the original image colors")
    parser.add_argument("--inverse", action="store_true", help="Change it so darker pixels relate to bigger chars")
    parser.add_argument("--font_path", type=str, default="", help="Path to font used by text (if any). Defaults to default paths for common OS fonts")
    parser.add_argument("--text_margin",  type=int, default=10, help="Size of margin of text. May be innacurate for different fonts. Defaults to 10 pixels")
    args = parser.parse_args()

    print_as_ascii(
        args.filepath, 
        new_width=args.width, 
        contrast_factor=args.contrast, 
        pixel_density=args.pixel_density, 
        inverse=args.inverse, 
        text_above=args.text_above, 
        text_below=args.text_below, 
        config=VideoConfig(
            skip_frames=args.skip_frames, 
            repeat=args.repeat, 
            time_bewtween_frames=args.time_between_frames
        ),
        color=args.color,
        font_path=args.font_path,
        text_margin=args.text_margin,
        brightness_factor=args.brightness
    )

if __name__ == "__main__":
    main()