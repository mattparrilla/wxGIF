#!/usr/bin/env python

from PIL import Image, ImageDraw, ImageFont
import os
import arrow

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

new_colors = [(0, 0, 0, 255),
    (50, 0, 0, 255),
    (100, 0, 0, 255),
    (158, 1, 66, 255),
    (213, 62, 79, 255),
    (244, 109, 67, 255),
    (253, 174, 97, 255),
    (254, 224, 139, 255),
    (255, 255, 191, 255),
    (230, 245, 152, 255),
    (171, 221, 164, 255),
    (102, 194, 165, 255),
    (50, 136, 189, 255),
    (94, 79, 162, 255),
    # Below colors are mostly white
    (150, 150, 150, 150),
    (150, 150, 150, 130),
    (150, 150, 150, 110),
    (150, 150, 150, 90),
    (150, 150, 150, 70),
    (150, 150, 150, 50),
    (150, 150, 150, 30),
    (255, 255, 255, 0)]


def change_palette(image):
    """Takes a list of dicts of images {'name': name, 'image': PIL.Image}
    converts the NWS palette to a new palette, returns list of filenames"""

    name = image.split('.')[0].split('/')[-1]
    im = Image.open(image).convert("RGBA")
    pixels = im.load()

    for i in range(im.size[0]):
        for j in range(im.size[1]):
            if pixels[i, j] in nws_colors:
                pixels[i, j] = new_colors[nws_colors.index(pixels[i, j])]

    filename = "gif/new_palette/%s.%s" % (name, "png")
    im.save(filename, "PNG")

    return filename


def resize_image(image, dimensions):
    im = Image.open(image)
    im.thumbnail(dimensions)
    return im


#def change_basemap(filename="basemap/northeast-outline.png"):
#    im = Image.open(filename)
#    pixels = im.load()
#    print pixels[0, 1]
#    for i in range(im.size[0]):
#        for j in range(im.size[1]):
#            if pixels[i, j] == (134, 134, 134, 127):
#                pixels[i, j] = (255, 255, 255, 0)
#
#    filename = "basemap/test.PNG"
#    im.save(filename, "PNG", dpi=[100, 100])


def add_basemap(radar, timestamp, region):
    basemap = "basemap/%s.png" % region
    background = basemap_text(Image.open(basemap), region)
    foreground = add_timestamp(radar, timestamp, region)
    combined = "gif/basemap/%s-bm-%s.png" % (
        basemap.split('/')[-1].split('.')[0],
        timestamp.replace(':', ''))

    background.paste(foreground, (0, 0), foreground)
    background.convert("P").save(combined, "PNG", optimize=True)

    return combined


def get_timestamp(filename, zone):
    time = filename.split('/')[-1].split('_')[2]
    utc_offset = arrow.now(zone).utcoffset()
    delta_t = utc_offset.days * 24 + utc_offset.seconds / 3600
    hour = int(time[:2]) + delta_t
    if hour < 0:
        hour += 24
    hour = str(hour)
    minutes = time[2:]
    timestamp = hour + ':' + minutes
    return timestamp


def add_timestamp(image, timestamp, region):
    draw = ImageDraw.Draw(image)
    w, h = image.size
    x_pos = 10
    color = (100, 100, 100)
    if region == 'northeast':
        y_pos = 40
    elif region == 'Conus':
        y_pos = h - 40
        x_pos = 10
        color = (50, 50, 50)
    else:
        y_pos = 10

    font = ImageFont.truetype('fonts/rokkitt.otf', 22)
    draw.text((x_pos, y_pos), timestamp, color, font=font)
    return image


def basemap_text(image, region):
    """Adds branding to image"""
    draw = ImageDraw.Draw(image)
    w, h = image.size
    font = ImageFont.truetype('fonts/raleway.otf', 55)
    small_font = ImageFont.truetype('fonts/raleway.otf', 18)

    if region == 'Conus':
        draw.text((10, h - 23), "@wxGIF", (50, 50, 50), font=small_font)
        draw.text((w - 210, h - 23), "Radar, made for Twitter",
            (50, 50, 50), font=small_font)
        return image

    if region in ['southeast', 'southplains', 'pacsouthwest']:
        x_pos = 20  # move branding to left side
    else:
        x_pos = w - 220

    if region in ['southrockies']:
        y_pos = h - 200
    else:
        y_pos = h - 100

    if region in ['northeast', 'southeast', 'southmissvly', 'pacsouthwest']:
        color = (250, 250, 250)
    else:
        color = (100, 100, 100)

    draw.text((x_pos, y_pos), "@wxGIF", color, font=font)
    draw.text((x_pos + 5, y_pos + 62), "Radar, made for Twitter", color, font=small_font)
    return image


def crop_image(image, region):
    cropped = Image.open(image)
    w, h = cropped.size
    x, y = 0, 0
    if region == 'northeast':
        y = 40
    elif region == 'southrockies':
        h = h - 100
    cropped.crop((x, y, w, h)).save(image, "PNG", optimize=True)
    return image


def change_projection(f, old_projection='EPSG:4269', new_projection='EPSG:3857'):
    """Change the projection of the GIF with accompanying world file
    By default changes NWS projection to Google Mercator"""

    path, extension = f.split('.')
    filename = path.split('/')[-1]
    new_path = 'gif/new_projection'
    gdalwarp = 'gdalwarp -s_srs %s -t_srs %s %s %s/%s-proj.%s' % (
        old_projection, new_projection, f, new_path, filename, extension)
    os.system(gdalwarp)

    return "%s/%s-proj.%s" % (new_path, filename, extension)
