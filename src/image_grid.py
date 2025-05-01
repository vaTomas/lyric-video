import random
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


def create_image_grid(
    mode, size, background_color, grid_size: int, grid_color, labeled: bool = False
):
    image = Image.new(mode, size, background_color)
    draw = ImageDraw.Draw(image)

    grid_points = []
    for xn in range((size[0] // grid_size) + 1):
        for yn in range((size[1] // grid_size) + 1):
            grid_points.append((xn * grid_size, yn * grid_size))

    # for _ in range(10):
    #     grid_points.append((random.randint(0, size[0]), random.randint(0, size[1])))

    print(grid_points)

    for grid_point in grid_points:
        x, y = grid_point
        draw.line(((x, 0), (x, size[1])), grid_color)
        draw.line(((0, y), (size[0], y)), grid_color)

    if labeled:
        font = ImageFont.truetype("calibri.ttf")
        for grid_point in grid_points:
            draw.text(
                grid_point,
                text=str(grid_point),
                font=font,
                anchor="mm",
                align="center",
                fill="black",
            )

    return image


def main():
    image = create_image_grid(
        mode="RGB",
        size=(1000, 1000),
        background_color="white",
        grid_size=100,
        grid_color="lightgrey",
        labeled=True,
    )
    image.show()


if __name__ == "__main__":
    main()
