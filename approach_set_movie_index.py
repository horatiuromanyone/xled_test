"""
in this version, we set the movie index and assume there are a bunch of movies already loaded on the twinkly,
"""


#from xled_plus.samples.sample_setup import *
# we do our own setup script so we can use the multicontrol rather than the highcontrol
import time

from xled.discover import xdiscover
from xled_plus.multicontrol import MultiHighControlInterface

print("started")


def setup_control():
    dev = xdiscover()

    # DO THIS BETTER THO
    hardcoded_device_count = 2

    the_list_of_devices = []

    for i in range(hardcoded_device_count):
        d = next(dev)
        print("Device: " + str(d))
        the_list_of_devices.append(d)

    print("found the " + str(hardcoded_device_count) + " devices")

    hostlst = [d.ip_address for d in the_list_of_devices]
    mhci = MultiHighControlInterface(hostlst)

    # stop querying dev
    dev.close()

    return mhci


def clamp(v, a, b):
    return min(max(v, a), b)


# init multicontrol and set movie mode. set frame in a loop
ctr = setup_control()
ctr.set_mode("movie")

NUM_MOVIES = 10

cur_time = 0
dtdir = 1
fps = 30
duration_per_movie = 5
duration = duration_per_movie * NUM_MOVIES
# get system time
system_time = time.time()
prev_time = system_time
while True:
    system_time = time.time()
    dt = system_time - prev_time # the DELTA TIME
    prev_time = system_time

    cur_time += dtdir * dt / duration
    cur_time = clamp(cur_time, 0, 1)
    if cur_time >= 1:
        dtdir = -1
    elif cur_time <= 0:
        dtdir = 1

    movie_index = clamp(int(cur_time * NUM_MOVIES), 0, NUM_MOVIES - 1)

    # set the movie index
    ctr.set_movies_current(movie_id=movie_index)

    # if the time since before setting is less than 0.1s, wait the remainder
    time_since_set = time.time() - prev_time
    if time_since_set < 1/fps:
        time.sleep(1/fps)

    # cur_time with 2 decimals
    print("INDEX " + str(movie_index) + " TIME " + str(round(cur_time, 2)))


