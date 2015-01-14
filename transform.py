#!/usr/bin/env python

import os
import json
from PIL import Image, ImageDraw, ImageFont

nws_colors = [(152, 84, 198, 255),
    (248, 0, 253, 255),
    (188, 0, 0, 255),
    (212, 0, 0, 255),
    (253, 0, 0, 255),
    (253, 139, 0, 255),
    (229, 188, 0, 255),
    (253, 248, 2, 255),
    (0, 142, 0, 255),
    (1, 197, 1, 255),
    (2, 253, 2, 255),
    (3, 0, 244, 255),
    (1, 159, 244, 255),
    (4, 233, 231, 255),
    # Below colors are mostly white
    (225, 225, 225, 255),
    (227, 227, 227, 255),
    (230, 230, 230, 255),
    (232, 232, 232, 255),
    (235, 235, 235, 255),
    (238, 238, 238, 255),
    (240, 240, 240, 255),
    (255, 255, 255, 255)]

negatives = [
    (150, 150, 150, 60),
    (150, 150, 150, 30),
    (150, 150, 150, 0),
    (150, 150, 150, 0),
    (150, 150, 150, 0),
    (150, 150, 150, 0),
    (150, 150, 150, 0),
    (255, 255, 255, 0)]

new_rainbow = [
    (138, 35, 117),
    (147, 41, 128),
    (161, 61, 142),
    (176, 79, 156),
    (76, 134, 178),
    (93, 148, 192),
    (110, 162, 207),
    (114, 184, 160),
    (128, 196, 173),
    (141, 209, 185),
    (211, 207, 182),
    (221, 218, 192),
    (230, 227, 201),
    (204, 204, 204)]

bl_gr_yl_rd_lt2dk = [
    (222, 235, 247, 200),
    (198, 219, 239, 255),
    (161, 217, 155, 255),
    (116, 196, 118, 255),
    (65, 171, 93, 255),
    (227, 26, 28, 255),
    (189, 0, 38, 255),
    (128, 0, 38, 255)]

blgrylrd_dk2lt = [
    (8, 48, 107, 255),
    (8, 81, 156, 255),
    (35, 139, 69, 255),
    (65, 171, 93, 255),
    (116, 196, 118, 255),
    (254, 178, 76, 255),
    (252, 187, 161, 255),
    (254, 224, 210, 255)]




def change_projection(filename, old_projection='EPSG:4269',
                      new_projection='EPSG:3857'):

    """Change the projection of the GIF using the appropraite world file and
    the command-line tool `gdalwarp`. By default changes NWS projection to
    Google Mercator"""

    print "Changing projection of %s" % filename

    path, extension = filename.split('.')
    name = path.split('/')[-1]
    new_path = 'gif/new_projection'
    gdalwarp = 'gdalwarp -s_srs %s -t_srs %s %s %s/%s-proj.%s' % (
        old_projection, new_projection, filename, new_path, name, extension)
    os.system(gdalwarp)

    return "%s/%s-proj.%s" % (new_path, name, extension)


def change_palette(image, color_scheme='YlGnBu'):
    """Takes an image file and changes the palette"""

    with open('palettes.json', 'r') as f:
        palettes = json.load(f)

    palette = expand_palette(palettes[color_scheme])[::-1]  # reverse list
    #palette = expand_palette(bl_gr_yl_rd_lt2dk[::-1])

    name = image.split('.')[0].split('/')[-1]
    im = Image.open(image).convert("RGBA")

    pixels = im.load()

    for i in range(im.size[0]):
        for j in range(im.size[1]):
            if pixels[i, j] in nws_colors:
                index = nws_colors.index(pixels[i, j])

                # The first 14 colors of the NWS palette correspond to positive
                # DBZ values (so rain clouds).
                if index < 14:
                    pixels[i, j] = palette[index]

                # The rest of the colors are mostly transparent greys
                elif index > 0:
                    pixels[i, j] = negatives[index - 14]

    filename = "gif/new_palette/%s.%s" % (name, "png")
    im.save(filename, "PNG")

    return filename


def expand_palette(palette):
    """Takes a colorbrewer palette of length 8 and uses it to build a palette
    of 14 colors."""

    new_palette = [0] * 15  # is 15 instead of 14 to create upper bound

    for i, color in enumerate(palette):
        new_palette[2 * i] = tuple(color)

    for i, color in enumerate(new_palette):
        if not color:
            r1, g1, b1, a1 = new_palette[i - 1]
            r2, g2, b2, a2 = new_palette[i + 1]
            new_r = (r1 + r2) / 2
            new_g = (g1 + g2) / 2
            new_b = (b1 + b2) / 2
            new_a = (a1 + a2) / 2
            new_palette[i] = (new_r, new_g, new_b, new_a)

    return new_palette


def add_basemap(radar, regions='Conus', basemap="basemap/Conus.png"):
    """Add Conus basemap and copy (via `add_text`) underneath radar image"""

    print "Adding basemap to %s" % radar

    timestamp = radar.split('/')[-1].split('_')[2]
    background = add_text(Image.open(basemap), timestamp, regions)
    foreground = Image.open(radar).convert("RGBA")
    combined = "gif/basemap/%s-bm-%s.png" % (
        basemap.split('/')[-1].split('.')[0], timestamp)

    background.paste(foreground, (0, 0), foreground)
    background.convert("P").save(combined, "PNG", optimize=True)

    return combined


def add_text(image, timestamp, regions='Conus', copy="wxGIF"):
    """Adds copy and timestamp for all regions to uncropped basemap"""

    timestamp = timestamp[:-2] + ':' + timestamp [-2:]
    draw = ImageDraw.Draw(image)
    color = (200, 200, 200)

    if regions == 'Conus':
        x1 = image.size[0] - 63
        x2 = image.size[0] - 63
        y1 = image.size[1] - 45
        y2 = image.size[1] - 25

        font = ImageFont.truetype('fonts/rokkitt.otf', 28)
        draw.text((x1, y1), timestamp, color, font=font)

        label_font = ImageFont.truetype('fonts/raleway.otf', 18)
        draw.text((x2, y2), copy, color, font=label_font)

    else:  # If regional imagery
        for region, attributes in regions.items():
            # attributes['corner'] uses cardinal directions, i.e. 'ne'
            if attributes['corner']:
                if 'n' in attributes['corner']:
                    y1 = attributes['coordinates'][1] + 5
                    y2 = attributes['coordinates'][1] + 25
                elif 's' in attributes['corner']:
                    y1 = attributes['coordinates'][3] - 45
                    y2 = attributes['coordinates'][3] - 25

                if 'w' in attributes['corner']:
                    x1 = attributes['coordinates'][0] + 10
                    x2 = attributes['coordinates'][0] + 10
                elif 'e' in attributes['corner']:
                    x1 = attributes['coordinates'][2] - 63
                    x2 = attributes['coordinates'][2] - 63

                font = ImageFont.truetype('fonts/rokkitt.otf', 28)
                draw.text((x1, y1), timestamp, color, font=font)

                label_font = ImageFont.truetype('fonts/raleway.otf', 18)
                draw.text((x2, y2), copy, color, font=label_font)

    return image
