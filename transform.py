#!/usr/bin/env python

import os
from PIL import Image


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


#def change_palette(image):
#    """Takes an image file and changes the palette"""
#
#    print "Changing palette of %s" % image
#
#    name = image.split('.')[0].split('/')[-1]
#    im = Image.open(image).convert("RGBA")
#
#    pixels = im.load()
#
#    for i in range(im.size[0]):
#        for j in range(im.size[1]):
#            if pixels[i, j] in nws_colors:
#                pixels[i, j] = new_colors[nws_colors.index(pixels[i, j])]
#
#    filename = "gif/new_palette/%s.%s" % (name, "png")
#    im.save(filename, "PNG")
#
#    return filename


def add_basemap(radar):
    """Add Conus basemap underneath radar image"""

    print "Adding basemap to %s" % radar

    timestamp = radar.split('/')[-1].split('_')[2]
    basemap = "basemap/Conus.png"
    foreground = Image.open(basemap)
    background = Image.open(radar)
    combined = "gif/basemap/%s-bm-%s.png" % (
        basemap.split('/')[-1].split('.')[0],
        timestamp.replace(':', ''))

    background.paste(foreground, (0, 0), foreground)
    background.show()
    background.convert("P").save(combined, "PNG", optimize=True)

    return combined
