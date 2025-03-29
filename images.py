import os
import random
from PIL import Image, ImageOps
from find_files_by_name import find_files_by_name as find_files


def place_images_randomly(input_images: list[str], canvas_size: tuple[int, int] = (1000,1000), max_rotation: int = 15, image_size = (100, 100)):
    """
    Places multiple square images at random locations with random rotations.

    Args:
        input_images (list[str]): List of paths to square input images.
        output_image_size (tuple[int, int]): Size of the output image (width, height).
        max_rotation (int): Maximum rotation angle (degrees).
    """
    output_image = Image.new("RGBA", canvas_size, (255, 255, 255, 0))  # Transparent background
    

    for image_path in input_images:
        try:
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)
            img = img.resize(image_size).convert("RGBA")
        except FileNotFoundError:
            print(f"Warning: Image file not found: {image_path}")
            continue

        rotation_angle = random.uniform(-max_rotation, max_rotation)
        img = img.rotate(rotation_angle, expand=True, resample=Image.BICUBIC) #expand and resample.

        x = random.randint(image_size[0], canvas_size[0] - image_size[0])
        y = random.randint(image_size[1], canvas_size[1] - image_size[1])

        if img.mode == "RGBA": #check if image has an alpha channel.
            output_image.paste(img, (x, y), img) # Use mask to handle transparency
        else:
            output_image.paste(img, (x,y)) # paste without mask if no alpha channel.

    output_image.save("output.png")


def main():
    # Example Usage
    path = "test/images"
    input_image_paths = find_files(path, ends_with='.jpg', search_subdir=True)  # Replace with your image paths
    output_size = (9000, 9000)
    image_size = (500, 500)

    try:
        place_images_randomly(input_image_paths, output_size, max_rotation=15, image_size=image_size)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()