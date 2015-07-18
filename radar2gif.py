from download_radar import download_images
from transform.palette import change_palette
from transform.projection import change_projection
from transform.basemap import add_basemap
from image_manipulation import crop, resize, resize_and_save
from libs.images2gif import writeGif
from PIL import Image
from config import (SAVE_TO_DIR, APP_KEY, APP_SECRET, twitter_keys)
from os.path import getsize
from twython import Twython
import json
from datetime import datetime


def radar_to_gif(tweet=False, max_number_of_frames=None):
    """Takes NWS radar imagery, changes palette, projection, adds a basemap
    and saves as a GIF.
    Optionally saves to S3 and publishes to twitter
    Source imagery: http://radar.weather.gov/GIS.html"""

    # Get data about all regions
    with open('regions.json', 'r') as f:
        regions = json.load(f)

    radar = download_images()[:max_number_of_frames]  # default is no max

    # Transform Radar
    reprojected = [change_projection(image) for image in radar if image is not None]
    new_palette = [change_palette(image) for image in reprojected]
    base_width = [resize_and_save(image) for image in new_palette]
    radar_and_basemap = [add_basemap(image, regions=regions) for image in base_width]

    # Create a list of gifs to be published
    gifs = []

    # Loop through regions, creating GIF
    for region, details in regions.items():
        cropped = [crop(image, details['coordinates'])
            for image in radar_and_basemap]
        resized = [resize(image) for image in cropped]
        gif = generate_gif(resized, region)
        hashtags = unpack_hashtags(details['hashtags'])
        gifs.append({'gif': gif, 'frames': resized, 'region': region,
            'hashtags': hashtags, 'name': details['name']})

    # Special case: continental united states does not need to be cropped
    conus_width = [resize_and_save(image, width=560) for image in new_palette]
    radar_and_conus = [add_basemap(image, basemap="basemap/Conus-sm.png")
        for image in conus_width]
    pil_objects = [Image.open(image) for image in radar_and_conus]
    gif = generate_gif(pil_objects, 'Conus')
    gifs.append({'gif': gif, 'frames': pil_objects, 'region': 'Conus',
        'hashtags': '#uswx #radar', 'name': "Continental US"})

    if tweet:
        for gif in gifs:
            tweet_gif(gif)


def unpack_hashtags(hashtag_list):
    """Takes a list of hashtags and adds a "#" before and a space after each"""

    hashtags = ""
    for tag in hashtag_list:
        hashtags += "#%s " % tag

    return hashtags


def generate_gif(images, name, duration=0.125):
    """Creates a gif from a list of PIL images"""

    gif_name = "%s/%s.gif" % (SAVE_TO_DIR, name)
    writeGif(gif_name, images, duration)
    return gif_name


def tweet_gif(gif, remove_frame=0):
    """Tweets the radar gif, includes region name and last radar image in tweet"""

    # If file too large, remove frames
    while getsize(gif['gif']) > 3000000:
        print "Resize necessary for %s: %s" % (gif['region'],
            getsize(gif['gif']))
        remove_frame += 1
        gif['gif'] = resize_gif(gif['region'], gif['frames'], remove_frame)

    # Connect to twitter API
    twitter = Twython(APP_KEY, APP_SECRET,
        twitter_keys[gif['region']]['OAUTH_TOKEN'],
        twitter_keys[gif['region']]['OAUTH_TOKEN_SECRET'])

    # Construct tweet content
    tweet = "Radar over the %s. %s" % (gif['name'], gif['hashtags'])
    photo = open(gif['gif'], 'rb')
    twitter.update_status_with_media(status=tweet, media=photo)

    print tweet
    print "Tweet sent at: " + datetime.now().strftime("%H:%M")


def resize_gif(region, frames, idx):
    """Removes frames from the beginning of the GIF"""

    thumbnail_f = '%s/%s.gif' % (SAVE_TO_DIR, region)
    writeGif(thumbnail_f, frames[idx:], duration=0.125)

    return thumbnail_f
