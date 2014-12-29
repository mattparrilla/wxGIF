from PIL import Image
import json
import os

#original_size = os.path.getsize('basemap/northeast-outline-708-3.png')
#original = Image.open('basemap/northeast-outline-708-3.png')
#
#print "Original file size: %s" % original_size
#
#size = (450, 450)
#original.thumbnail(size, Image.ANTIALIAS)
#original.save('test/thumbnail.png', "PNG")
#
#thumbnail_size = os.path.getsize('test/thumbnail.png')
#
#print "Thumbnail size: %s" % thumbnail_size
#
#optimize = Image.open('basemap/northeast-outline-708-3.png')
#optimize.save('test/optimize.png', "PNG", optimize=True)
#print "Optimized size: %s" % os.path.getsize('test/optimize.png')

#convert = Image.open('basemap/green-northeast-708.png')
#convert.convert('P').save('test/green.png', "PNG", optimize=True)
#print "Converted size: %s" % os.path.getsize('test/green.png')

#with open('regions.json', 'r') as f:
#  regions = json.load(f)
#
#new_dict = {}
#for k, v in regions['coordinates'][0].items():
#    for i, value in enumerate(v):
#        v[i] = int(value * 0.8)
#    new_dict[k] = {'coordinates': v, 'corner': 'nw'}
#
#with open('regionss.json', 'w') as f:
#   json.dump(new_dict, f)

with open('colorbrewer.json', 'r') as f:
    colorbrewer = json.load(f)

new_dict = {}
for palette, bins in colorbrewer.items():
    for number, colors in bins.items():
        if number == '8':
            for i, color in enumerate(colors):
                color += "ff"
                colors[i] = tuple(map(ord, color.decode('hex')))

            new_dict[palette] = colors

with open('palettes.json', 'w') as f:
   json.dump(new_dict, f)
