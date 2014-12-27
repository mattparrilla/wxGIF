from PIL import Image, ImageOps


def crop(image_file, coordinates):
    """Crops an image to the given coordinates, returns PIL object"""

    print "Cropping %s" % image_file

    image = Image.open(image_file)
    cropped = image.crop((coordinates[0], coordinates[1], coordinates[2],
            coordinates[3]))
    return cropped


def resize(image, width=560.0):
    """Resizes an image to a given width"""

    print "Resizing %s" % image
    original_width = image.size[0]
    original_height = image.size[1]
    height = width * original_height / original_width
    size = (int(width), int(height))
    im = ImageOps.fit(image, size, Image.ANTIALIAS)
    return im
