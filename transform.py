#!/usr/bin/env python

from PIL import Image
import os


def change_palette(filename, palette=False):
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
        (240, 240, 240, 255)]

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
        (104, 79, 162, 215),
        (114, 79, 162, 175),
        (124, 79, 162, 145),
        (134, 79, 162, 115),
        (144, 79, 162, 85),
        (144, 79, 162, 55),
        (154, 79, 162, 55)]

    im = Image.open(filename).convert("RGBA")
    pixels = im.load()

    for i in range(im.size[0]):
        for j in range(im.size[1]):
            if pixels[i, j] in nws_colors:
                pixels[i, j] = new_colors[nws_colors.index(pixels[i, j])]

    name = os.path.splitext(filename)[0]
    im.save("%s.%s" % (name, 'PNG'), "PNG")


def change_projection(f, old_projection='EPSG:4269', new_projection='EPSG:3857'):
    """Change the projection of the GIF with accompanying world file
    By default changes NWS projection to Google Mercator"""

    filename, extension = f.split('.')
    gdalwarp = 'gdalwarp -s_srs %s -t_srs %s %s %s_new.%s' % (old_projection,
        new_projection, f, filename, extension)
    os.system(gdalwarp)

    return "%s_new.%s" % (filename, extension)

change_projection('gif/target.gif')
