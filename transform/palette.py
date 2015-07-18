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

hcl = ["3D4979", "6F4E8B", "985495", "BA6193", "D37487", "E28E71",
          "E6AB55", "DDCB42"]

hcl_palette = [tuple(ord(c) for c in color.decode('hex')) for color in hcl]


def change_color(original_color, palette):
    """Takes an RGBA color from the NWS palette and returns a new RGBA color of
    the selected palette"""

    index = nws_colors.index(original_color)

    # The first 14 colors of the NWS palette correspond to positive
    # DBZ values (so rain clouds).
    if index < 14:
        new_color = palette[index]

    # The rest of the colors are mostly transparent greys
    elif index > 0:
        new_color = negatives[index - 14]

    else:
        new_color = original_color

    return new_color


def expand_palette(palette):
    """Takes an array of 8 colors and uses it to build a palette
    of 14 colors"""

    new_palette = [0] * 15  # is 15 instead of 14 to create upper bound

    for i, color in enumerate(palette):
        new_palette[2 * i] = tuple(color)

    for i, color in enumerate(new_palette):
        if not color:
            try:
                r1, g1, b1, a1 = new_palette[i - 1]
                r2, g2, b2, a2 = new_palette[i + 1]
            # exception occurs when palette doesn't have alpha channel
            except ValueError:
                r1, g1, b1 = new_palette[i - 1]
                a1 = 255
                r2, g2, b2 = new_palette[i + 1]
                a2 = 255
            new_r = (r1 + r2) / 2
            new_g = (g1 + g2) / 2
            new_b = (b1 + b2) / 2
            new_a = (a1 + a2) / 2
            new_palette[i] = (new_r, new_g, new_b, new_a)

    return new_palette

blue_yellow_red = expand_palette(hcl_palette[::-1])


def change_palette(image, palette=blue_yellow_red):
    """Takes an image file and changes the palette"""

    name = image.split('.')[0].split('/')[-1]
    im = Image.open(image).convert("RGBA")

    pixels = im.load()

    for i in range(im.size[0]):
        for j in range(im.size[1]):
            if pixels[i, j] in nws_colors:
                pixels[i, j] = change_color(pixels[i, j], palette)

    filename = "gif/new_palette/%s.%s" % (name, "png")
    im.save(filename, "PNG")

    return filename
