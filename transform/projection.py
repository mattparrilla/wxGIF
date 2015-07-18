import os


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
