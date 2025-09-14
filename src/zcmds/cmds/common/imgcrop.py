import argparse
import os

from PIL import Image


def main():
    parser = argparse.ArgumentParser(
        description="Crops an image based on specified dimensions."
    )
    parser.add_argument("input", help="Input image file.")
    parser.add_argument(
        "--bottom",
        type=int,
        default=0,
        help="Crop from the bottom by this many pixels. Use negative values to crop from the top.",
    )
    parser.add_argument(
        "--output", help="Output image file (default: input_cropped.ext)."
    )

    args = parser.parse_args()

    input_path = args.input
    bottom_crop = args.bottom

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return 1

    try:
        img = Image.open(input_path)
        width, height = img.size

        # Calculate the new height after cropping from the bottom
        # If bottom_crop is negative, it means crop from the top, so new_height will be height + bottom_crop
        # If bottom_crop is positive, it means crop from the bottom, so new_height will be height - bottom_crop
        new_height = height - bottom_crop

        if new_height <= 0:
            print(
                f"Error: Cropped image height would be zero or negative ({new_height}). Adjust --bottom value."
            )
            return 1

        # Define the cropping box (left, upper, right, lower)
        # Cropping from the bottom means the 'lower' coordinate changes
        # If bottom_crop is positive, we are removing from the bottom, so lower = new_height
        # If bottom_crop is negative, we are removing from the top, so upper = -bottom_crop
        if bottom_crop >= 0:
            # Crop from the bottom
            box = (0, 0, width, new_height)
        else:
            # Crop from the top (bottom_crop is negative, so -bottom_crop is positive)
            box = (0, -bottom_crop, width, height)

        cropped_img = img.crop(box)

        if args.output:
            output_path = args.output
        else:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_cropped{ext}"

        cropped_img.save(output_path)
        print(f"Image cropped and saved to '{output_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")
        return 1

    return 0


if __name__ == "__main__":
    main()
