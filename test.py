import geocoder
from pixy import *
from ctypes import *

myloc = geocoder.ip('me')
print(myloc.latlng)
