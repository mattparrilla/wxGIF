from PIL import Image
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

convert = Image.open('basemap/green-northeast-708.png')
convert.convert('P').save('test/green.png', "PNG", optimize=True)
print "Converted size: %s" % os.path.getsize('test/green.png')
