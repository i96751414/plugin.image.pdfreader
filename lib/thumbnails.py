import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from lib.api.pdf import utils

THUMBNAILS_FOLDER = os.path.join(utils.DATA_PATH, "thumbnails")
if not os.path.exists(THUMBNAILS_FOLDER):
    os.makedirs(THUMBNAILS_FOLDER)


def check_color(color):
    if color > 255:
        color = 255
    elif color < 0:
        color = 0
    return color


def generate_thumbnail(text, image_width, image_height, font_resource_file, font_size, font_color, background_color,
                       file_name, x_offset=0, y_offset=0, draw_shadow=False, shadow_color=0, iterations=5,
                       shadow_x_offset=5, shadow_y_offset=5):
    # Perform color checks
    background_color = check_color(background_color)
    font_color = check_color(font_color)

    # Convert the text into unicode
    text = utils.str_to_unicode(text)

    # Create character image:
    char_image = Image.new("L", (image_width, image_height), background_color)

    # Draw character image
    draw = ImageDraw.Draw(char_image)

    # Specify font : Resource file, font size
    font = ImageFont.truetype(font_resource_file, font_size)

    # Get character width and height
    (font_width, font_height) = font.getsize(text)

    # Calculate x position
    x = ((image_width - font_width) / 2) + x_offset

    # Calculate y position
    y = ((image_height - font_height) / 2) + y_offset

    # Draw shadow
    if draw_shadow and iterations > 0:
        shadow_color = check_color(shadow_color)

        shadow_color_step = float(shadow_color - background_color) / iterations
        shadow_x_step = float(shadow_x_offset) / iterations
        shadow_y_step = float(shadow_y_offset) / iterations
        for i in range(iterations, 0, -1):
            shadow_x = int(x + shadow_x_step * i)
            shadow_y = int(y + shadow_y_step * i)
            sh_color = int(shadow_color - shadow_color_step * i)
            draw.text((shadow_x, shadow_y), text, sh_color, font=font)

    # Draw text
    draw.text((x, y), text, font_color, font=font)

    # Save image
    char_image.save(file_name)


def get_thumbnail(text):
    thumbnail_path = os.path.join(THUMBNAILS_FOLDER, "%s.png" % text)
    if not os.path.exists(thumbnail_path):
        font_file = os.path.join(utils.ADDON_PATH, "resources", "fonts", "arial.ttf")
        generate_thumbnail(text, 512, 512, font_file, 200, 0, 160, thumbnail_path, draw_shadow=True)

    return thumbnail_path
