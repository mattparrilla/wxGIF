#!/usr/bin/env python
import requests
import shutil
import pytz
import os
import socket
import arrow
from os import listdir
from os.path import isfile, join
from PIL import Image
from datetime import datetime, timedelta
from libs.images2gif import writeGif
from bs4 import BeautifulSoup as Soup
from StringIO import StringIO
from twython import Twython
from transform import change_palette, change_projection, add_basemap

if socket.gethostname() == 'm' or socket.gethostname() == 'matt.local':
    from config import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    SAVE_TO_DIR = 'gif'
    bot = False
else:
    APP_KEY = os.environ['APP_KEY']
    APP_SECRET = os.environ['APP_SECRET']
    OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
    OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']
    SAVE_TO_DIR = '/tmp'
    bot = True

region_to_tz = {'northeast': 'US/Eastern'}
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

    #updated_radar = fresh_check(radar_urls[-1], 15)
    updated_radar = True

    if updated_radar:
        return regional_urls
    else:
        return False


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
    image_urls = get_region(region)
    images = []
    wf_url = "%s/%s_radaronly.gfw" % (BASE_URL, region)
    wf = requests.get(wf_url)
    for src in image_urls:
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
    return images


def make_gif(region, dimensions, resize=False):
#    if resize:
#        image_dir = "gif/completed_frames"
#        image_list = ["%s/%s" % (image_dir, f) for f in listdir(image_dir)
#            if isfile(join(image_dir, f)) and "DS_Store" not in f]
#
#    else:
    images = download_radar_images(region)
    new_projections = []
    for im in images:
        new_projections.append(change_projection(im))

    image_list = change_palette(new_projections)

    frames = resize_convert_images(image_list, dimensions, resize)

    filename = '%s/%s.gif' % (SAVE_TO_DIR, region)
    writeGif(filename, frames, duration=0.1)
    return filename


def resize_convert_images(image_list, dimensions, resize):
    frames = []
    for idx, image in enumerate(image_list):
#        if not resize:
        image = add_basemap(image)
        im = Image.open(image)
        im.thumbnail(dimensions, Image.ANTIALIAS)
        frames.append(im.convert("P"))
    return frames


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


def tweet_gif(region, size=450):
    """Tweets the radar gif, includes region name and last radar image in tweet"""

    current_hour = arrow.now(region_to_tz[region]).hour

    # if running manually or at appointed hour
    if not bot or current_hour in [0, 3, 6, 9, 12, 15, 18, 21]:
        gif = make_gif(region, dimensions=(size, size))
       # while os.path.getsize(gif) > 2900000:
       #     print "Resize Necessary: %s" % os.path.getsize(gif)
       #     size -= 20
       #     gif = make_gif(region, dimensions=(size, size), resize=True)

        time = last_updated_radar(get_region(region)[-1])

        if bot:
            twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            tweet = "Radar over the %s. Most recent image from %s ET #vtwx #nywx #mewx #ctwx #mawx #pawx #nhwx #nhwx #njwx" % (
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

tweet_gif('northeast')
