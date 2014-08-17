#!/usr/bin/env
import requests
import pytz
import os
from PIL import Image
from datetime import datetime
from images2gif import writeGif
from bs4 import BeautifulSoup as Soup
from StringIO import StringIO
from twython import Twython
from config import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

if not APP_KEY:
    APP_KEY = os.environ['APP_KEY']
    APP_SECRET = os.environ['APP_SECRET']
    OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
    OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']


def get_region(region_name):
    """Parses NWS Radar Image Directory (see: http://radar.weather.gov/GIS.html)
    for radar images of specified region"""

    url = 'http://radar.weather.gov/ridge/Conus/RadarImg/'
    r = requests.get(url)
    soup = Soup(r.text)

    radar_urls = []
    for link in soup.findAll("a"):
        href = link.get("href")
        if region_name in href and "20" in href and "N0Ronly" not in href:
            radar_urls.append(url + href)

    return radar_urls


def diff_from_utc(zone):
    eastern = pytz.timezone(zone)
    utc = pytz.utc
    now = datetime.now()
    delta = utc.localize(now) - eastern.localize(now)
    return delta


def make_gif(region_name):
    """Takes a list of image hrefs and turns them into an animated GIF
    returns path to gif and datetimeobject of most recent radar image"""

    image_hrefs = get_region(region_name)

    images = []
    for href in image_hrefs:
        r = requests.get(href)
        images.append(Image.open(StringIO(r.content)))

    size = (450, 450)
    for im in images:
        im.thumbnail(size, Image.ANTIALIAS)

    utc_stamp = datetime.strptime(image_hrefs[-1][-8:-4], "%H%M")
    time = utc_stamp + diff_from_utc('US/Eastern')

    filename = './gif/%s-%s.GIF' % (region_name,
        datetime.now().strftime('%Y%m%d-%H%M'))
    writeGif(filename, images, duration=0.1)
    return filename, time


def obtain_auth_url():
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


def tweet_gif(region):
    """Tweets the radar gif, includes region name and last radar image in tweet"""

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    gif, time = make_gif(region)
    photo = open(gif, 'rb')
    tweet = "Radar over the %s for the past few hours. Most recent image from %s #wx #GIF" % (
        region.title(), time.strftime("%I:%M%p").lstrip("0"))
    twitter.update_status_with_media(status=tweet, media=photo)

tweet_gif("northeast")
