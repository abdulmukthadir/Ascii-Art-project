"""
Matrix ASCII Art Generator
---------------------------
Converts any image into ASCII art and prints it in a Matrix-style green
terminal theme. Also saves the plain ASCII output to a text file.

Usage:
    python main.py cat.jpg
    python main.py cat.jpg -w 150
    python main.py cat.jpg -o result.txt
    python main.py cat.jpg --no-color
    python main.py cat.jpg --invert
"""

import argparse
import sys
from PIL import Image
from colorama import init, Fore, Style

# Characters ordered from darkest to lightest.
# Dark pixels get "heavy" characters like @, light pixels get spaces/dots.
ASCII_CHARS = "@%#*+=-:. "


def autocrop_dark_border(image, threshold=15):
    """Crop away near-black borders/background so the ASCII output isn't
    wasted on empty space.
    """
    gray = image.convert("L")
    # Treat anything darker than threshold as 'background' to be cropped
    bbox = gray.point(lambda p: 255 if p > threshold else 0).getbbox()
    return image.crop(bbox) if bbox else image


def resize_image(image, new_width=100):
    """Resize the image to fit the terminal, correcting for character shape.

    Terminal characters are taller than they are wide, so without this
    correction the ASCII output looks stretched vertically.
    """
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio * 0.55)
    return image.resize((new_width, max(new_height, 1)))


def grayscale_image(image):
    """Convert image to grayscale so each pixel is a single brightness value."""
    return image.convert("L")


def pixels_to_ascii(image, invert=False):
    """Map each pixel's brightness (0-255) to a character in ASCII_CHARS.

    If invert=True, dark pixels get light characters (spaces/dots) and
    bright pixels get heavy characters (@). This works well for dark
    images viewed on a dark terminal background, since the background
    becomes empty space instead of a solid block of @.
    """
    chars = ASCII_CHARS[::-1] if invert else ASCII_CHARS
    pixels = image.getdata()
    characters = "".join(
        chars[pixel * (len(chars) - 1) // 255] for pixel in pixels
    )
    return characters


def image_to_ascii(image_path, new_width=100, invert=False):
    """Full pipeline: load -> crop -> resize -> grayscale -> map to characters."""
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error: could not open image '{image_path}': {e}")
        sys.exit(1)

    image = autocrop_dark_border(image)
    image = resize_image(image, new_width)
    image = grayscale_image(image)

    ascii_str = pixels_to_ascii(image, invert)

    # Break the long character string into rows of `new_width` characters
    pixel_count = len(ascii_str)
    ascii_rows = [
        ascii_str[i:i + new_width] for i in range(0, pixel_count, new_width)
    ]
    return "\n".join(ascii_rows)


def print_matrix(ascii_art):
    """Print the ASCII art in bright green (the 'Matrix' look)."""
    init()  # needed for colors to work correctly on some terminals
    print(Fore.GREEN + Style.BRIGHT + ascii_art + Style.RESET_ALL)


def save_ascii(ascii_art, output_path):
    """Save the plain (uncolored) ASCII art to a text file."""
    with open(output_path, "w") as f:
        f.write(ascii_art)
    print(f"\nSaved ASCII art to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert an image into Matrix-style green ASCII art."
    )
    parser.add_argument("image", help="Path to the image file (jpg, png, etc.)")
    parser.add_argument(
        "-w", "--width", type=int, default=100,
        help="Width of the ASCII output in characters (default: 100)"
    )
    parser.add_argument(
        "-o", "--output", default="output.txt",
        help="File to save the ASCII art to (default: output.txt)"
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="Print plain ASCII without the matrix green color"
    )
    parser.add_argument(
        "--invert", action="store_true",
        help="Invert brightness mapping (good for dark images on a dark terminal)"
    )

    args = parser.parse_args()

    ascii_art = image_to_ascii(args.image, args.width, args.invert)

    if args.no_color:
        print(ascii_art)
    else:
        print_matrix(ascii_art)

    save_ascii(ascii_art, args.output)


if __name__ == "__main__":
    main()