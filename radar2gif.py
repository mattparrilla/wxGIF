#!/usr/bin/env python
import requests
import pytz
import os
import socket
import arrow
from PIL import Image
from datetime import datetime, timedelta
from libs.images2gif import writeGif
from bs4 import BeautifulSoup as Soup
from StringIO import StringIO
from twython import Twython
from transform import change_palette, change_projection

if socket.gethostname() == 'm' or socket.gethostname() == 'matt.local':
    from config import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    save_to_dir = 'gif'
    bot = False
else:
    APP_KEY = os.environ['APP_KEY']
    APP_SECRET = os.environ['APP_SECRET']
    OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
    OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']
    save_to_dir = '/tmp'
    bot = True

region_to_tz = {'northeast': 'US/Eastern'}


def get_all_radar_urls():
    # get document with list of radar image locations
    url = 'http://radar.weather.gov/ridge/Conus/RadarImg/'
    r = requests.get(url)
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
    base_url = 'http://radar.weather.gov/ridge/Conus/RadarImg/'

    regional_urls = []
    radar_urls = get_all_radar_urls()
    # URL has form http://[url]/regionname_YYYYMMDD_HHMM.gif
    for href in radar_urls:
        if region_name in href and "20" in href and "N0Ronly" in href:
            regional_urls.append(base_url + href)

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


def make_gif(image_urls, dimensions):
    """Takes a list of image hrefs and turns them into an animated GIF
    returns path to gif and datetimeobject of most recent radar image"""

    images = []
    for src in image_urls:
        r = requests.get(src)
        try:
            images.append({'name': src.split('/')[-1],
                'image': Image.open(StringIO(r.content)).convert("RGBA")})
        except IOError:
            print "IOError: " + str(r.status_code)
            continue

    image_list = change_palette(images)

    transformed_images = []
    for image in image_list:
        im = change_projection(image)
        transformed_images.append(Image.open(im))

    #size = (dimensions, dimensions)
    #for im in images:
    #    im.thumbnail(size, Image.ANTIALIAS)

    filename = '%s/%s' % (save_to_dir, image_urls[-1].split('/')[-1])
    writeGif(filename, transformed_images, duration=0.1)
    return filename


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


def tweet_gif(region, size=600):
    """Tweets the radar gif, includes region name and last radar image in tweet"""

    current_hour = arrow.now(region_to_tz[region]).hour

    # if running manually or at appointed hour
    if not bot or current_hour in [0, 3, 6, 9, 12, 15, 18, 21]:
        radar_urls = get_region(region)
        gif = make_gif(radar_urls, size)
        while os.path.getsize(gif) > 9000000:
            size -= 50
            gif = make_gif(radar_urls, size)

        time = last_updated_radar(radar_urls[-1])

        if bot:
            twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            tweet = "Radar over the %s. Most recent image from %s ET #vtwx #nywx #mewx #ctwx #mawx #pawx #nhwx #vawx #nhwx #njwx" % (
                region.title(), time)
            photo = open(gif, 'rb')
            twitter.update_status_with_media(status=tweet, media=photo)
            print tweet
            print "Tweet sent at: " + datetime.now().strftime("%H:%M")

tweet_gif('northeast')
