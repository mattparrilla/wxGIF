#!/bin/bash

cd /home/mattparrilla/git/wxgif/app && source venv/bin/activate && /home/mattparrilla/git/wxgif/app/venv/bin/python2.7 radar2gif.py && rm gif/basemap/* && rm gif/source/* && rm gif/new_palette/* rm gif/new_projection/* && deactivate
