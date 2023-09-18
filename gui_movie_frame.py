"""
I'm using the GUI library PySimpleGUI to make a simple GUI.
I'm using xled-plus for better controls of the xled device.
In this script I check the mouse position and normalize X axis based on the size of the window
I set movie mode on the device and set the seek() to the mouse_position.x so we control the movie frame
"""
import io
import math

import PySimpleGUI as sg

layout = [
    [sg.Text("page setter")],
    [sg.Text("mouse pos", key="mousepos")],
    [sg.Button("OK")],
]

# Create the window
window = sg.Window("REAL", layout, finalize=True)
# bind to mouse move event
window.bind('<Motion>', 'Motion')


# xled stuff
# init xled_plus
from xled_plus.samples.sample_setup import *
ctr = setup_control()
ctr.set_mode("movie")

# which movie to control
movie_index = ctr.get_movies_current()
all_movies = ctr.get_movies()["movies"]
the_movie = all_movies[movie_index]
movie_data = ctr.show_movie()

def init_device():
    return


def clamp(v, a, b):
    return min(max(v, a), b)


def set_page(page01):
    global movie_index

    cur_movie = ctr.get_movies_current()
    movies = ctr.get_movies()

    # the movie length in frames
    the_movie = movies["movies"][movie_index]
    movie_frame_count = the_movie["frames_number"]
    page01 = clamp(page01, 0, 1)
    target_frame = int(movie_frame_count * page01)
    print("seek to " + str(target_frame))

    # I searched and searched and I couldn't find a way to set which frame of the movie to display.


    return


# Create an event loop
while True:
    event, values = window.read()

    if event == "Motion":
        # cursor position in window
        mouse_pos = window.mouse_location()
        window_pos = window.current_location()
        # window size
        window_size = window.size
        # normalized mouse position
        mouse_xy_01 = ((mouse_pos[0] - window_pos[0]) / window_size[0], (mouse_pos[1] - window_pos[1]) / window_size[1])

        set_page(mouse_xy_01[0])

        # update mouse position in text UI
        # position with 2 decimals
        window["mousepos"].update("mouse pos: " + str(round(mouse_xy_01[0], 2)) + ", " + str(round(mouse_xy_01[1], 2)))

    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
