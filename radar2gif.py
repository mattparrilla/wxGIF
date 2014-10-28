#!/usr/bin/env python
import requests
import shutil
import pytz
import os
import sys
from PIL import Image
from datetime import datetime, timedelta
from libs.images2gif import writeGif
from bs4 import BeautifulSoup as Soup
from twython import Twython
from config import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
from transform import (change_palette, change_projection, add_basemap,
    resize_image, crop_image, get_timestamp)

if len(sys.argv) > 1:
    bot = False

else:
    bot = True


SAVE_TO_DIR = 'gif'
BASE_URL = 'http://radar.weather.gov/ridge/Conus/RadarImg/'


def get_all_radar_urls():
    # get document with list of radar image locations
    r = requests.get(BASE_URL)
    soup = Soup(r.text)

    # parse the document, pulling only relevant images
    radar_urls = []
    for link in soup.findAll("a"):
        href = link.get("href")
        radar_urls.append(href)

    return radar_urls


def get_region(region_name):
    """Parses NWS Radar Image Directory (see: http://radar.weather.gov/GIS.html)
    for radar images of specified region"""

    regional_urls = []
    radar_urls = get_all_radar_urls()
    # URL has form http://[url]/regionname_YYYYMMDD_HHMM.gif
    for href in radar_urls:
        if region_name in href and "20" in href and "N0Ronly" in href:
            regional_urls.append(BASE_URL + href)

    return regional_urls


def check_freshness(url, minutes):
    """Given a URL, gets the last-modified date of the resource and returns true
    if the resource has been modified within N minutes
    Currently no longer using this method. Could be useful during weather events
    or maybe never."""

    r = requests.get(url)
    last_modified = r.headers['last-modified']
    lm = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S GMT")
    time_updated = (datetime.utcnow() - lm).seconds

    fresh = (minutes * 60) > time_updated

    return fresh


def diff_from_utc(zone):
    eastern = pytz.timezone(zone)
    utc = pytz.utc
    now = datetime.now()
    delta = utc.localize(now) - eastern.localize(now)
    return delta


def download_radar_images(region):
    print "Downloading radar images and world file"
    image_urls = get_region(region)
    images = []
    wf_url = "%s/%s_radaronly.gfw" % (BASE_URL, region)
    wf = requests.get(wf_url)
    for src in image_urls:
        print "Downloading: %s" % src
        r = requests.get(src, stream=True)
        if r.status_code == 200:
            name = "gif/source/%s" % src.split('/')[-1]
            wf_name = "%s.gfw" % name.split('.')[0]
            with open(name, "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            with open(wf_name, "wb") as f:
                f.write(wf.text)
            images.append(name)

    print "All images downloaded"
    return images


def make_gif(region, dimensions):
    images = download_radar_images(region)

    print "\nChanging radar projection"
    new_projections = [change_projection(im) for im in images]

    print "\nChanging radar palette"
    image_list = [change_palette(im) for im in new_projections]
    print "Done"

    print "\nGet timestamps"
    timestamps = [get_timestamp(image, region) for image in image_list]

    print "\nResize Image"
    thumbnails = [resize_image(image, dimensions) for image in image_list]

    print "\nAdding basemap"
    frames = [add_basemap(image, timestamps[idx], region) for idx,
        image in enumerate(thumbnails)]
    print "Done"

    print "\nCropping image"
    cropped = [crop_image(image) for image in frames]
    print "Done"

    print "\nConvert image format"
    cropped_frames = [Image.open(im) for im in cropped]

    print "\nMaking GIF"
    filename = '%s/%s.gif' % (SAVE_TO_DIR, region)
    writeGif(filename, cropped_frames, duration=0.125)

    return filename, cropped_frames


def resize_gif(region, frames, idx):
    thumbnail_f = '%s/%s.gif' % (SAVE_TO_DIR, region)
    writeGif(thumbnail_f, frames[idx:], duration=0.125)

    return thumbnail_f


def last_updated_radar(url):
    time_of_radar = url.split('/')[-1].split('.')[0].split('_')[-2]
    radar_datetime = (datetime.strptime(time_of_radar, "%H%M") +
        timedelta(days=365))
    time_in_est = radar_datetime + diff_from_utc('US/Eastern')
    last_radar_time = time_in_est.strftime("%I:%M").lstrip("0")
    return last_radar_time


def obtain_auth_url():
    """Used to app to tweet to my account
    NOT CALLED ANYWHERE"""
    twitter = Twython(APP_KEY, APP_SECRET)
    auth = twitter.get_authentication_tokens()

    oauth_token = auth['oauth_token']
    oauth_token_secret = auth['oauth_token_secret']
    print "\n\n\nGo to the following URL to authorize app:"
    print auth['auth_url']
    oauth_verifier = raw_input("\nEnter the pin: ")

    twitter = Twython(APP_KEY, APP_SECRET, oauth_token, oauth_token_secret)
    authorized = twitter.get_authorized_tokens(oauth_verifier)

    #write confirmed tokens to disk
    with open("config.py", "a") as config_file:
        config_file.write("\nOAUTH_TOKEN = '" + authorized['oauth_token']
            + "'\nOAUTH_TOKEN_SECRET = '" + authorized['oauth_token_secret'] + "'")


def tweet_gif(region, size=(450, 585), remove_frame=0):
    """Tweets the radar gif, includes region name and last radar image in tweet"""

    # if running manually or at appointed hour
    gif, frames = make_gif(region, size)
    while os.path.getsize(gif) > 3000000:
        print "Resize Necessary: %s" % os.path.getsize(gif)
        remove_frame += 1
        gif = resize_gif(region, frames, remove_frame)

    time = last_updated_radar(get_region(region)[-1])

    if bot:
        twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        tweet = "Radar over the %s. Most recent image from %s ET #vtwx #nywx #mewx #ctwx #mawx #pawx #nhwx #njwx #skitheeast" % (
            region.title(), time)
        photo = open(gif, 'rb')
        twitter.update_status_with_media(status=tweet, media=photo)
        print tweet
        print "Tweet sent at: " + datetime.now().strftime("%H:%M")


def get_map_bounds(region_name):
    base_url = 'http://radar.weather.gov/ridge/Conus/RadarImg/'
    map_dimensions = (840, 800)
    radar_urls = get_all_radar_urls()
    for href in radar_urls:
        if region_name in href and ".gfw" in href:
            gfw = href

    r = requests.get(base_url + gfw)
    gfw = r.text.replace('\r', '').split('\n')
    for i, x in enumerate(gfw):
        gfw[i] = float(x)

    top_left_coords = (gfw[4], gfw[5])
    bottom_right_coords = ((gfw[4] + map_dimensions[0] * gfw[0]),
        (gfw[5] + map_dimensions[1] * gfw[3]))

    print "The bounding coordinates are (%f, %f) and (%f, %f)" % (
        top_left_coords[0], top_left_coords[1], bottom_right_coords[0],
        bottom_right_coords[1])
    print "%f,%f,%f,%f" % (top_left_coords[0], bottom_right_coords[1],
        bottom_right_coords[0], top_left_coords[1])

tweet_gif('northrockies')
