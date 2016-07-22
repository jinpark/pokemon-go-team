from PIL import Image

# requires tesseract-ocr
import pyocr
import pyocr.builders
import difflib

import pokemondata

TOP_CROP = 0.13644
ROW_SIZE = 0.232
COLUMN_SIZE = 0.33

TOOL = pyocr.get_available_tools()[0]

def crop_cp(image):
    img_width = image.size[0]
    img_height = image.size[1]
    return image.crop((0, 0, img_width, img_height * 0.25))

def crop_name(image):
    img_width = image.size[0]
    img_height = image.size[1]
    return image.crop((0, img_height * 0.72, img_width, img_height))

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

def ocr_image(file):
    pokemon_dict = {"pokemon": [], "edited": False }
    all_pokemon_text = []

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
            name_text = TOOL.image_to_string(
                name,
                lang="eng",
                builder=pyocr.builders.TextBuilder()
            )
            cp_text = TOOL.image_to_string(
                cp,
                lang="eng",
                builder=pyocr.builders.TextBuilder()
            )
            cp_cleaned_text = "".join([ c if c.isalnum() else "\n" for c in cp_text ])
            probable_cp = int(max(cp_cleaned_text.splitlines(), key=len).lower().replace('cp', '').split()[0])
            name_cleaned_text = max(name_text.splitlines(), key=len).lower()
            probable_name = "".join(name_cleaned_text.split())
            spell_checked_name = difflib.get_close_matches(probable_name, pokemondata.all_pokemon_names, 1, 0.8) or [probable_name]

            print([probable_cp, spell_checked_name])
            pokemon_dict["pokemon"].append({"cp": probable_cp, "nickname": spell_checked_name[0]})

    return pokemon_dict
