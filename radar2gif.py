#!/usr/bin/env python
import requests
import pytz
import os
import socket
from PIL import Image
from datetime import datetime
from images2gif import writeGif
from bs4 import BeautifulSoup as Soup
from StringIO import StringIO
from twython import Twython

if socket.gethostname() == 'm':
    from config import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    save_to_dir = 'gif'
else:
    APP_KEY = os.environ['APP_KEY']
    APP_SECRET = os.environ['APP_SECRET']
    OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
    OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']
    save_to_dir = '/tmp'


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

    updated_radar = fresh_check(radar_urls[-1], 10)

    if updated_radar:
        return radar_urls
    else:
        return False


def fresh_check(url, minutes):
    """Given a URL, gets the last-modified date of the resource and returns true
    if the resource has been modified within N minutes"""
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


def make_gif(region_name):
    """Takes a list of image hrefs and turns them into an animated GIF
    returns path to gif and datetimeobject of most recent radar image"""

    fresh_images = get_region(region_name)
    if fresh_images:
        # need time of radar in addition to last-modified time b/c time of
        # radar not always time image was uploaded
        time_of_radar = fresh_images[-1][-8:-4]  # gets the time from filename
        radar_datetime = datetime.strptime(time_of_radar, "%H%M")
        time_in_est = radar_datetime + diff_from_utc('US/Eastern')

        images = []
        for src in fresh_images:
            r = requests.get(src)
            images.append(Image.open(StringIO(r.content)))

        size = (450, 450)
        for im in images:
            im.thumbnail(size, Image.ANTIALIAS)

        filename = '%s/%s-%s.GIF' % (save_to_dir, region_name,
            datetime.now().strftime('%Y%m%d-%H%M'))
        writeGif(filename, images, duration=0.1)
        return filename, time_in_est

    else:
        return False, False


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
    if gif:
        photo = open(gif, 'rb')
        tweet = "Radar over the %s for the past few hours. Most recent image from %s #wx #GIF" % (
            region.title(), time.strftime("%I:%M%p").lstrip("0"))
        twitter.update_status_with_media(status=tweet, media=photo)
        print "Tweet sent at: " + datetime.now().strftime("%H:%M")
    else:
        print "Radar not fresh"

tweet_gif("northeast")
