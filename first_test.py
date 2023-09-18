"""
This is a test file to see if I can control the XLED device.
I can connect to it, set the movie mode and set the index of which movie should play.
 also more stuff that's in the xled package.
"""

import xled

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


# set movie is a way to set an LED
# movie = #not sure what is a movie yet.
# control_high.set_led_movie_full(movie)

if True:
    # see the current amount of effects, you can prob switch between them n stuff.
    led_effects = control_high.get_led_effects()
    print("got effects. code: " + str(led_effects['code']) + "; effects_number: " + str(led_effects["effects_number"]))
    for leuid in led_effects["unique_ids"]:
        print(leuid)

    print("")

    # see the amount of movies loaded.
    movies = control_high.get_movies()
    print("found " + str(len(movies)) + " movies")
    for movie in movies:
        print(movie)

    # movies is an array with all the data for each movie
    print(movies["movies"])
    # available_frames is a number based on the memory of the device - more LEDs, less memory
    print(movies["available_frames"])
    print(movies["max_capacity"])
    # dunno what max means. it's 55 when I have 2x2 squares. maybe it's the amount of files or kb it can hold?
    print(movies["max"])
    print(movies["code"])

    # mode (str) – Mode to set. One of ‘movie’, ‘playlist’, ‘rt’, ‘demo’, ‘effect’, ‘color’ or ‘off’.
    control_high.set_mode("movie")
    control_high.set_movies_current(0)


# rt sounds like "real-time". can control it in realtime but gotta figure out the format for a frame...
# control_high.set_mode("rt")
# frame = ""
# control_high.set_rt_frame_socket(frame, version=3)
