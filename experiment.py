from PIL import Image
from palettes.colorbrewer import NEW_PALETTE
from palettes.nws import NWS_PALETTE

def change_palette(image, old_palette, new_palette):
    """Take a paletted image with known colors and change palettes"""

    # getpalette() returns a list of 768 ints; 768 / 3 = 256 = the # of colors
    # doesn't return 3 item (r, g, b) tuple for whatever reason
    palette = image.getpalette()

    # loop through each color
    for j in range(len(palette) / 3):
        i = j * 3  # i is the index of the color in the getpalette list
        rgb = (palette[i], palette[i + 1], palette[i + 2])
        if rgb in old_palette:
            palette_index = old_palette.index(rgb)
            new_color = new_palette[palette_index]
            for k in range(3):
                palette[i + k] = new_color[k]

    image.putpalette(palette)
    return image

test_image = Image.open('gif/source/Conus_20150112_1408_N0Ronly.gif')
new_image = change_palette(test_image, NWS_PALETTE, NEW_PALETTE)
new_image.show()
