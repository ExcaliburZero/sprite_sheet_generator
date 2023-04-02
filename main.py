from dataclasses import dataclass
from typing import cast, List

import argparse
import sys

import PIL.Image
import PIL.ImageDraw

SUCCESS = 0


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_images", nargs="+", required=True)
    parser.add_argument("--output_image", required=True)
    parser.add_argument("--width", type=int, default=1000)
    parser.add_argument("--border_width", type=int, default=1)
    parser.add_argument("--border_color", default="green")

    args = parser.parse_args(argv)

    result = validate_args(input_images=args.input_images)
    if result != SUCCESS:
        return result

    sheet = SpriteSheet.from_image_filepaths(
        args.input_images,
        args.width,
        args.border_width,
    )

    sheet.to_image(args.border_color).save(args.output_image)
    print("Wrote output image to:", args.output_image)

    return SUCCESS


def validate_args(input_images: List[str]) -> int:
    return SUCCESS


Color = str


@dataclass
class SpriteSheet:
    images: List[List[PIL.Image.Image]]
    width: int
    border_width: int

    def to_image(self, border_color: Color) -> PIL.Image.Image:
        image = PIL.Image.new("RGBA", (self.width, self.height))

        self.__paste_images(image)
        self.__add_borders(image, border_color)

        return image

    def __paste_images(self, output_image: PIL.Image.Image) -> None:
        current_height = self.border_width
        for row in self.images:
            current_width = self.border_width
            for image in row:
                location = (current_width, current_height)
                output_image.paste(image, location)

                current_width += image.width + self.border_width

            row_height = SpriteSheet.calc_row_image_height(row)
            current_height += row_height + self.border_width

    def __add_borders(self, output_image: PIL.Image.Image, border_color: Color) -> None:
        draw = PIL.ImageDraw.Draw(output_image)

        current_height = self.border_width
        for row in self.images:
            current_width = self.border_width
            for image in row:
                location = (current_width, current_height)
                output_image.paste(image, location)

                dimensions = (
                    current_width - self.border_width,
                    current_height - self.border_width,
                    current_width + image.width,
                    current_height + image.height,
                )

                draw.rectangle(
                    dimensions,
                    width=self.border_width,
                    outline=border_color,
                )

                current_width += image.width + self.border_width

            row_height = SpriteSheet.calc_row_image_height(row)
            current_height += row_height + self.border_width

    @property
    def height(self) -> int:
        border_spacing = self.border_width * len(self.images)
        image_spacing = 0
        for row in self.images:
            image_spacing += max((img.height for img in row))

        return border_spacing + image_spacing

    @staticmethod
    def from_image_filepaths(
        filepaths: List[str], width: int, border_width: int
    ) -> "SpriteSheet":
        image_list = [PIL.Image.open(filepath) for filepath in filepaths]

        images: List[List[PIL.Image.Image]] = [[]]
        for img in image_list:
            image_width_plus_border = img.width + 2 * border_width
            if image_width_plus_border > width:
                raise ValueError(
                    f"Found images that was wider than allowed width when accounting for border: ({img.width} + 2 * {border_width} > {width})"
                )

            potential_row = images[-1].copy() + [img]

            if SpriteSheet.calc_row_width(potential_row, border_width) <= width:
                images[-1].append(img)
                continue

            images.append([img])

        # Truncate width to only needed width for images + border
        actual_width = max(
            (SpriteSheet.calc_row_width(row, border_width) for row in images)
        )

        return SpriteSheet(images, actual_width, border_width)

    @staticmethod
    def calc_row_width(row: List[PIL.Image.Image], border_width: int) -> int:
        border_spacing = (len(row) + 1) * border_width
        image_spacing = sum((image.width for image in row))

        return border_spacing + image_spacing

    @staticmethod
    def calc_row_image_height(row: List[PIL.Image.Image]) -> int:
        return max((img.height for img in row))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
