"""
This is a utility script that clears all movies from the Twinkly device.
"""

from xled_plus.samples.sample_setup import *
ctr = setup_control()

ctr.clear_movies()

print("Cleared!")