#!/usr/bin/env python

import os
from PIL import Image

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


def change_palette(image):
    """Takes an image file and changes the palette"""

    print "Changing palette of %s" % image

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


def add_basemap(radar, basemap="basemap/Conus.png"):
    """Add Conus basemap underneath radar image"""

    print "Adding basemap to %s" % radar

    timestamp = radar.split('/')[-1].split('_')[2]
    background = Image.open(basemap)
    foreground = Image.open(radar).convert("RGBA")
    combined = "gif/basemap/%s-bm-%s.png" % (
        basemap.split('/')[-1].split('.')[0],
        timestamp.replace(':', ''))

    background.paste(foreground, (0, 0), foreground)
    background.convert("P").save(combined, "PNG", optimize=True)

    return combined
