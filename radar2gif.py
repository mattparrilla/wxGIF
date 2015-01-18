#!/usr/bin/env python

from download_radar import download_images
from transform import change_projection, add_basemap, change_palette
from image_manipulation import crop, resize, resize_and_save
from libs.images2gif import writeGif
from PIL import Image
from config import SAVE_TO_DIR
from os import listdir
from os.path import isfile, join
import json


def radar_to_gif(publish=False, tweet=False):
    """Takes NWS radar imagery, changes palette, projection, adds a basemap
    and saves as a GIF.
    Optionally saves to S3 and publishes to twitter
    Source imagery: http://radar.weather.gov/GIS.html"""

    # Get data about all regions
    with open('regions.json', 'r') as f:
        regions = json.load(f)

    radar = download_images()

    # mypath and following line used to skip steps when testing new styles
    #mypath = "gif/new_projection"
    #reprojected = ["%s/%s" % (mypath, f) for f in listdir(mypath)
    #    if isfile(join(mypath, f)) and f != '.DS_Store']

    # Transform Radar
    reprojected = [change_projection(image) for image in radar]
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
            'hashtags': hashtags})

    # Special case: continental united states does not need to be cropped
    conus_width = [resize_and_save(image, width=560) for image in new_palette]
    radar_and_conus = [add_basemap(image, basemap="basemap/Conus-sm.png")
        for image in conus_width]
    pil_objects = [Image.open(image) for image in radar_and_conus]
    gif = generate_gif(pil_objects, 'Conus')
    gifs.append({'gif': gif, 'frames': pil_objects, 'region': 'Conus',
        'hashtags': '#uswx #radar'})

    ## Get time of last radar image
    #last_radar = radar_and_basemap[-1]
    #time_of_image = last_radar.split('/')[-1].split('.')[0].split('-')[-1]
    #radar_datetime = (datetime.strptime(time_of_image, "%H%M") +
    #    timedelta(days=365))

    if publish:
        for gif in gifs:
            publish(gif)

    if tweet:
        for gif in gifs:
            tweet_gif(gif)


#def diff_from_utc(zone):
#    """Returns diff between UTC and supplied timezone"""
#
#    timezone = pytz.timezone(zone)
#    utc = pytz.utc
#    now = datetime.now()
#    delta = utc.localize(now) - timezone.localize(now)
#    return delta


def unpack_hashtags(hashtag_list):
    """Takes a list of hashtags and adds a "#" before and a space after each"""

    hashtags = ""
    for tag in hashtag_list:
        hashtags += "#%s " % tag

    return hashtags


def generate_gif(images, name, duration=0.125):
    """Creates a gif from a list of PIL images"""

    gif_name = "%s/%s.gif" % (SAVE_TO_DIR, name)
    gif = writeGif(gif_name, images, duration)
    return gif


def tweet_gif(gif, remove_frame=0):
    """Tweets the radar gif, includes region name and last radar image in tweet"""

    # If file too large, remove frames
    while os.path.getsize(gif) > 3000000:
        print "Resize Necessary: %s" % os.path.getsize(gif)
        remove_frame += 1
        gif = resize_gif(gif['region'], gif['frames'], remove_frame)

    # Connect to twitter API
    twitter = Twython(APP_KEY, APP_SECRET,
        twitter_keys[region]['OAUTH_TOKEN'],
        twitter_keys[region]['OAUTH_TOKEN_SECRET'])

    # Construct tweet content
    tweet = "Radar over the %s. %s" % (region_name[region], hashtags[region])
    photo = open(gif['gif'], 'rb')
    #twitter.update_status_with_media(status=tweet, media=photo)

    print tweet
    print "Tweet sent at: " + datetime.now().strftime("%H:%M")


def resize_gif(region, frames, idx):
    """Removes frames from the beginning of the GIF"""

    thumbnail_f = '%s/%s.gif' % (SAVE_TO_DIR, region)
    writeGif(thumbnail_f, frames[idx:], duration=0.125)

    return thumbnail_f

radar_to_gif(tweet=True)
