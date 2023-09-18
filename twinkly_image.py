"""
an attempt to make a script that can send an image to the twinkly device.
failed for now.
"""

import xled
import sys

print("started")
print("version " + xled.__version__)
discovered_device = xled.discover.discover()
print("found device")
print(discovered_device)
print("device id: " + discovered_device.id)

# if discovered, use this to control the device
control_high = xled.HighControlInterface(discovered_device.ip_address, discovered_device.hw_address)
control = xled.ControlInterface(discovered_device.ip_address, discovered_device.hw_address)
print("is on? " + str(control_high.is_on()))

# see cli.py to see how to use the CLI commands in script
# such as turn_on, turn_off, set_timer, set_movie, set_color, etc

if not control_high.is_on():
    control_high.turn_on()

# control set_mode() can be: 'movie', 'playlist', 'rt', 'demo', 'effect' or 'off'.

control_high.set_mode('movie')

# when running this script in the CLI, get the first arg
if len(sys.argv) > 1:
    path_to_image = sys.argv[1]
else:
    path_to_image = "img/gr_med.jpg"

# convert the image to a movie
control_high.set_movies_new("img123", "1515151", "rgb_raw", 256, 1, 1)
#doesn't wokr!!!?!?!?!