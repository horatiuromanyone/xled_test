"""
I'm using the GUI library PySimpleGUI to make a simple GUI.
Inside, I check the mouse position and normalize based on the size of the window
I start a realtime mode on the xled device, and I update each frame with colors based on the coordinate of the led
when the mouse hits the led with the same normalized coordinate, I draw white, else the color.
I update all the LEDs every update. which is why it might be a bit slow.
"""
import io
import math

from xled_plus.samples.sample_setup import *

class HoratiuEffect(Effect):
    def __init__(self, ctr):
        super(HoratiuEffect, self).__init__(ctr)
        self.pat = None

        self.preferred_frames = 2
        self.preferred_fps = 8

        self.mouse_xy_01 = (0, 0) # normalized mouse position in window

    def reset(self, numframes=False):
        self.pat = self.ctr.make_func_pattern(lambda i: rgb_color(0, 0, 0))

    def layout_pattern(self, pos, ind):
        #print("mxy " + str(self.mouse_xy_01) + " pos " + str(pos))
        # pos is between -1.0, 1.0

        grid_size = 16

        # flip y axis on mouse
        mouse_xy_01_flipped = (self.mouse_xy_01[0], 1 - self.mouse_xy_01[1])

        # quantize the mouse position to the grid
        mouse_xy_01_quantized = (round(mouse_xy_01_flipped[0] * grid_size) / grid_size, round(mouse_xy_01_flipped[1] * grid_size) / grid_size)
        # quantize the pos to the grid
        pos_quantized = (round(pos[0] * grid_size) / grid_size, round(pos[1] * grid_size) / grid_size)

        # if mouse pos in grid is same as pos in grid, return white
        if mouse_xy_01_quantized == pos_quantized:
            return rgb_color(1, 1, 1)

        return rgb_color(pos[0], pos[1], -pos[0])

    def getnext(self):
        #ctr.make_solid_pattern(rgb_color(0, 0, 0))
        new_la_pattern = ctr.make_layout_pattern(
            lambda pos, ind: self.layout_pattern(pos, ind)
            , index=True)
        self.pat = new_la_pattern

        return self.pat


# setup and run the thing, and also shut it down when done
ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
eff = HoratiuEffect(ctr)
oldmode = ctr.get_mode()["mode"]
eff.launch_rt()
print("Started continuous effect - press Return to stop it (or close window)")
# input()
# eff.stop_rt()
# ctr.set_mode(oldmode)






import xled
import PySimpleGUI as sg

layout = [
    [sg.Text("it REAL")],
    #[sg.Button("-")],
    #[sg.Button("+")],
    # text where we can output the mouse position
    [sg.Text("mouse pos", key="mousepos")],
    [sg.Text("window pos", key="windowpos")],
    [sg.Button("OK")],
]

# Create the window
window = sg.Window("REAL", layout, finalize=True)
# bind to mouse move event
window.bind('<Motion>', 'Motion')


def on_press(delta):
    # nothing
    pass

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

        eff.mouse_xy_01 = mouse_xy_01

        # update mouse position in text UI
        # position with 2 decimals
        window["mousepos"].update("mouse pos: " + str(round(mouse_xy_01[0], 2)) + ", " + str(round(mouse_xy_01[1], 2)))
        window["windowpos"].update("window pos: " + str(window_pos))


    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

eff.stop_rt()
ctr.set_mode(oldmode)

window.close()
