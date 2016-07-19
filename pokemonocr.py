from PIL import Image

# requires tesseract-ocr
import pyocr
import pyocr.builders

TOP_CROP = 0.15
ROW_SIZE = 0.23
COLUMN_SIZE = 0.33

def crop_cp(image):
    img_width = image.size[0]
    img_height = image.size[1]
    return image.crop((0, 0, img_width, img_height * 0.4))

def crop_name(image):
    img_width = image.size[0]
    img_height = image.size[1]
    return image.crop((0, img_height * 0.6, img_width, img_height))

def crop_row(image, row):
    img_width = image.size[0]
    img_height = image.size[1]
    return image.crop((0, row * img_height * ROW_SIZE, img_width, img_height * ROW_SIZE * (row + 1)))

def crop_column(image, column):
    img_width = image.size[0]
    img_height = image.size[1]
    return image.crop( (column * img_width * COLUMN_SIZE + (img_width * COLUMN_SIZE * 0.1), 0, (column + 1) * img_width * COLUMN_SIZE - (img_width * COLUMN_SIZE * 0.1), img_height ) )


# remove top row with the tabs and status bar

ROWS = 2
COLUMNS = 3

all_pokemon_text = []

def ocr_image(file):
    tool = pyocr.get_available_tools()[0]

    img = Image.open(file)
    img_width = img.size[0]
    img_height = img.size[1]

    pokemon_only = img.crop((0, img_height * TOP_CROP, img_width, img_height))

    for row in range(ROWS):
        row_image = crop_row(pokemon_only, row)
        for column in range(COLUMNS):
            column_image = crop_column(row_image, column)
            cp = crop_cp(column_image)
            name = crop_name(column_image)
            cp_text = tool.image_to_string(
                cp,
                lang="eng",
                builder=pyocr.builders.TextBuilder()
            )
            name_text = tool.image_to_string(
                name,
                lang="eng",
                builder=pyocr.builders.TextBuilder()
            )
            all_pokemon_text.append({"cp": int(max(cp_text.splitlines(), key=len).lower().replace('cp', '').split()[0]), "name": max(name_text.splitlines(), key=len).lower()})

    return all_pokemon_text
