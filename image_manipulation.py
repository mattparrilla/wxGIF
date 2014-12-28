from PIL import Image, ImageOps


def crop(image_file, coordinates):
    """Crops an image to the given coordinates, returns PIL object"""

    print "Cropping %s" % image_file

    # New basemap is 80% of size of previous basemap, so region coordinates
    # need to be scaled accordingly
    scaled_coords = [int(i * 0.8) for i in coordinates]

    image = Image.open(image_file)
    cropped = image.crop((scaled_coords[0], scaled_coords[1], scaled_coords[2],
            scaled_coords[3]))

    return cropped


def resize(image, width=560.0):
    """Resizes an image to a given width"""

    original_width = image.size[0]
    original_height = image.size[1]
    height = width * original_height / original_width
    size = (int(width), int(height))
    im = ImageOps.fit(image, size, Image.ANTIALIAS)
    return im


def resize_and_save(image, width=2240.0):
    """Takes a file path, opens in PIL, resizes, converts to RGBA and returns
    a file path"""

    im = Image.open(image)
    resized_image = resize(im, width)
    resized_image.save(image, "PNG", optimize=True)
    return image
