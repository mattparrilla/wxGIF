from PIL import Image, ImageDraw, ImageFont
import arrow


def add_basemap(radar, regions='Conus', basemap="basemap/Conus.png"):

    """Add Conus basemap and copy (via `add_text`) underneath radar image"""

    print "Adding basemap to %s" % radar

    timestamp = radar.split('/')[-1].split('_')[2]
    print basemap
    background = add_text(Image.open(basemap), timestamp, regions)
    foreground = Image.open(radar).convert("RGBA")
    combined = "gif/basemap/%s-bm-%s.png" % (
        basemap.split('/')[-1].split('.')[0], timestamp)

    background.paste(foreground, (0, 0), foreground)
    background.convert("P").save(combined, "PNG", optimize=True)

    return combined


def add_text(image, timestamp, regions='Conus', copy="wxGIF"):
    """Adds copy and timestamp for all regions to uncropped basemap"""

    draw = ImageDraw.Draw(image)
    color = (200, 200, 200)

    if regions == 'Conus':
        x1 = image.size[0] - 63
        x2 = image.size[0] - 63
        y1 = image.size[1] - 42
        y2 = image.size[1] - 25

        time = convert_to_timezone(timestamp, 'US/Eastern')

        font = ImageFont.truetype('fonts/DroidSansMono.ttf', 16)
        draw.text((x1, y1), time, color, font=font)

        label_font = ImageFont.truetype('fonts/raleway.otf', 18)
        draw.text((x2, y2), copy, color, font=label_font)

    else:  # If regional imagery
        for region, attributes in regions.items():
            time = convert_to_timezone(timestamp, attributes['timezone'])
            # attributes['corner'] uses cardinal directions, i.e. 'ne'
            if attributes['corner']:
                if 'n' in attributes['corner']:
                    y1 = attributes['coordinates'][1] + 8
                    y2 = attributes['coordinates'][1] + 25
                elif 's' in attributes['corner']:
                    y1 = attributes['coordinates'][3] - 42
                    y2 = attributes['coordinates'][3] - 25

                if 'w' in attributes['corner']:
                    x1 = attributes['coordinates'][0] + 9
                    x2 = attributes['coordinates'][0] + 10
                elif 'e' in attributes['corner']:
                    x1 = attributes['coordinates'][2] - 63
                    x2 = attributes['coordinates'][2] - 63

                font = ImageFont.truetype('fonts/DroidSansMono.ttf', 16)
                draw.text((x1, y1), time, color, font=font)

                label_font = ImageFont.truetype('fonts/raleway.otf', 18)
                draw.text((x2, y2), copy, color, font=label_font)

    return image


def convert_to_timezone(time, timezone):
    """Takes a UTC timestamp of HHMM format and converts to specified TZ in
    format: HH:MM"""

    utc_offset = arrow.now(timezone).utcoffset()
    delta_t = utc_offset.days * 24 + utc_offset.seconds / 3600
    hour = int(time[:2]) + delta_t

    # delta_t will be negative, so negative time values possible
    if hour < 0:
        hour += 24

    hour = str(hour)
    minutes = time[2:]
    timestamp = hour + ":" + minutes

    return timestamp
