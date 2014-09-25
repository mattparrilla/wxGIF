#Weather GIFs

This project generates GIFs of NWS radar images and auto tweets them at regular times. Currently only tweeting GIFs of the northeast at the twitter handle [@wxGIF](http://twitter.com/wxgif).

Very much a work in progress. Feel free to pull and contribute or clone and use it yourself!

##To Make Your Own GIF

Currently, you'd probably need to be a developer (or at least are able to use the command line) but I have plans to create a web interface in the future (see below)

Dependencies: `gdal`, `virtualenv`, `pip`

Here are the current steps (to be entered in the command line) required to generate a GIF for the northeast:

1. `git clone git@github.com:mattparrilla/wxGIF.git`
2. `cd wxGIF`
3. `virtualenv venv`
4. `source venv/bin/activate`
5. `pip install -r requirements.txt`
6. `python radar2gif.py`

Look inside the `gif/` directory and you'll see `northeast.gif` the full-sized GIF of the radar for the northeast. `northeast-twitter.gif` is a twitter-sized version of the same image (twitter requires GIFs to be below 3MB in size in order to upload them via the API).

##Next Steps

1. Abstract/clean code for other users
2. Document steps from clone to tweet
3. Increase quality of image
3. Create twitter account for each region
3. Only tweet when some threshold of activity
4. Get working with individual radar stations
5. ~~Change base map + projection~~
6. ~~Change color palette.~~
7. Incorporate warnings/watches
8. Turn into web app

##License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this work except in compliance with the License.
You may obtain a copy of the License in the LICENSE file, or at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language
governing permissions under the License.
