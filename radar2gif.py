#!/usr/bin/env python

from download_radar import download_images
from transform import change_projection, add_basemap, change_palette
from image_manipulation import crop, resize, resize_and_save
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

    # Get data about all regions
    with open('regions.json', 'r') as f:
        regions = json.load(f)

    #radar = download_images()

    # Transform Radar
    mypath = "gif/new_projection"
    reprojected = ["gif/new_projection/%s" % f for f in listdir(mypath) if isfile(join(mypath, f)) and f != '.DS_Store']
    #reprojected = [change_projection(image) for image in radar]
    new_palette = [change_palette(image) for image in reprojected]
    base_width = [resize_and_save(image) for image in new_palette]
    radar_and_basemap = [add_basemap(image, regions) for image in base_width]

    # Create a list of gifs to be published
    gifs = []


    # Loop through regions, creating GIF
    for region, details in regions.items():
        cropped = [crop(image, details['coordinates'])
            for image in radar_and_basemap]
        resized = [resize(image) for image in cropped]
        gif = generate_gif(resized, region)
        gifs.append(gif)

    # Special case: continental united states does not need to be cropped
    #conus_width = [resize_and_save(image, width=560) for image in new_palette]
    #radar_and_conus = [add_basemap(image, "basemap/Conus-sm.png")
    #    for image in conus_width]
    ##conus_with_text = [add_text(image) for image in resized_conus]
    #pil_objects = [Image.open(image) for image in radar_and_conus]
    #gif = generate_gif(pil_objects, 'Conus')
    #gifs.append(gif)

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
