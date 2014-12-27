#!/usr/bin/env python

from download_radar import download_images
from transform import change_projection, add_basemap, change_palette
from image_manipulation import crop, resize
from libs.images2gif import writeGif
from PIL import Image
from config import SAVE_TO_DIR
import json

from os import listdir
from os.path import isfile, join


def radar_to_gif(publish=False, tweet=False):
    """Takes NWS radar imagery, changes palette, projection, adds a basemap
    and saves as a GIF.
    Optionally saves to S3 and publishes to twitter
    Source imagery: http://radar.weather.gov/GIS.html"""

    # radar = download_images()

    # Transform Radar
    # reprojected = [change_projection(image) for image in radar]
    mypath = "gif/new_projection"
    onlyfiles = ["gif/new_projection/%s" % f for f in listdir(mypath) if isfile(join(mypath, f)) and f != '.DS_Store']
    new_palette = [change_palette(image) for image in onlyfiles]
    radar_and_basemap = [add_basemap(image) for image in new_palette]

    # Create a list of gifs to be published
    gifs = []

    # Get data about all regions
    with open('regions.json', 'r') as f:
        regions = json.load(f)

    # Loop through regions, creating GIF
    for region, coordinates in regions['coordinates'][0].items():
        cropped = [crop(image, coordinates) for image in radar_and_basemap]
        resized = [resize(image) for image in cropped]
        #region_with_text = [add_text(image) for image in resized]
        gif = generate_gif(resized, region)
        gifs.append(gif)

    # Special case: continental united states does not need to be cropped
    resized_conus = [resize(Image.open(image)) for image in radar_and_basemap]
    #conus_with_text = [add_text(image) for image in resized_conus]
    gif = generate_gif(resized_conus, 'Conus')
    gifs.append(gif)

    if publish:
        for gif in gifs:
            publish(gif)

    if tweet:
        for gif in gifs:
            tweet(gif)


def generate_gif(images, name, duration=0.125):
    """Creates a gif from a list of PIL images"""

    gif_name = "%s/%s.gif" % (SAVE_TO_DIR, name)
    gif = writeGif(gif_name, images, duration)
    return gif

radar_to_gif()
