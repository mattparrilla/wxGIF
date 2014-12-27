#!/usr/bin/env python

from bs4 import BeautifulSoup as Soup
from config import BASE_URL
import requests
import shutil


def download_images():
    """Controller function that gets a list of images at BASE_URL and downloads
    the images associated with the Continental United States (Conus) radar."""

    print "Downloading radar images and world file"
    radar_src = get_all_radar_urls()
    conus_src = get_conus(radar_src)
    world_file_url = "%s/latest_radaronly.gfw" % BASE_URL
    world_file = requests.get(world_file_url).text

    saved_radar = [save_radar(image, world_file) for image in conus_src]

    return saved_radar


def save_radar(src, world_file):
    """Save a radar image and a world file, giving the world file the same
    name as the radar image"""

    r = requests.get(src, stream=True)
    if r.status_code == 200:
        name = "gif/source/%s" % src.split('/')[-1]  # split leaves file.ext
        gfw = "%s.gfw" % name.split('.')[0]  # same name but ext .gfw

        # Save image
        with open(name, "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        # Save world file
        with open(gfw, "wb") as f:
            f.write(world_file)

        return name


def get_all_radar_urls():
    """Get and return a list of all image hrefs at BASE_URL"""

    # Get document with list of radar image locations
    r = requests.get(BASE_URL)
    soup = Soup(r.text)

    # Parse the document, pulling only relevant images
    radar_urls = []
    for link in soup.findAll("a"):
        href = link.get("href")
        radar_urls.append(href)

    return radar_urls


def get_conus(radar_urls):
    """Parses NWS Radar Image Directory for Conus imagery"""

    conus_urls = []

    # URL has form http://.../Conus_YYYYMMDD_HHMM.gif
    for href in radar_urls:
        if 'Conus' in href and "20" in href and "N0Ronly" in href:
            conus_urls.append(BASE_URL + href)

    return conus_urls
