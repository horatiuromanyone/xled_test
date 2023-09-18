"""
in this test, we generate fake input left/right with the mouse, and
we write to the console every time the input changes and when the getnext() function runs.
we can see that it's very infrequent and there is some mad bottleneck in the code somewhere in the xled library
or maybe even in the twinkly socket implementation, it's waiting for a response or whatev??!?! anyway it's unreasonably slow...
"""

# Movie hack:
# use ffmpeg to change the format, resolution and stuff
# ffmpeg -i nomove.mov -vf scale=24:32 -c:v libx264 -crf 15 -g 1 nomove2.mp4


# read the movie file into memory
import math

import cv2
import sys

#path_to_video = "img/video32x34.mov"

path_to_video = "img/video4kstausadjusted.mp4"
# path_to_video = "img/sag1.mov"
# path_to_video = "img/nomove2.mp4"

# path_to_video = "img/pixely.mov"
# path_to_video = "img/pixely2.mp4"
# ffmpeg -i pixely.mov -vf scale=240:320 -c:v libx264 -crf 15 -g 1 pixely3.mp4
# path_to_video = "img/pixely3.mp4"

#path_to_video = "img/trimmed.mov"

FRAMERATE = 6

sin_time = 0

# get video from path
the_video = cv2.VideoCapture(path_to_video)
print("Loaded video: " + path_to_video)

# get the amount of frames in the video
the_video_frame_count = int(the_video.get(cv2.CAP_PROP_FRAME_COUNT))
print("Frame count: " + str(the_video_frame_count))

# the output resolution of the LED screen :)
# maybe we can get this info from xled?
# NOTE: we can't because it doesn't assume it's a square. it can have wacky shapes.
output_res = (24, 32)

# initialize array of size output_res[0] * output_res[1] * 3 * number of frames
frames_cached = bytearray(output_res[0] * output_res[1] * 3 * the_video_frame_count)


def set_frame_sample(frame_index, x, y, r, g, b):
    global frames_cached
    frames_cached[frame_index * output_res[0] * output_res[1] * 3 + (y * output_res[0] + x) * 3 + 0] = r
    frames_cached[frame_index * output_res[0] * output_res[1] * 3 + (y * output_res[0] + x) * 3 + 1] = g
    frames_cached[frame_index * output_res[0] * output_res[1] * 3 + (y * output_res[0] + x) * 3 + 2] = b


def get_frame_sample(frame_index, x, y):
    global frames_cached
    return frames_cached[frame_index * output_res[0] * output_res[1] * 3 + (y * output_res[0] + x) * 3 + 0], \
           frames_cached[frame_index * output_res[0] * output_res[1] * 3 + (y * output_res[0] + x) * 3 + 1], \
           frames_cached[frame_index * output_res[0] * output_res[1] * 3 + (y * output_res[0] + x) * 3 + 2]


def clamp(v, a, b):
    return min(max(v, a), b)


# get frame from video
def get_frame(video: cv2.VideoCapture, frame_index: int):
    frame_index = clamp(frame_index, 0, the_video_frame_count - 1)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video.read()
    return frame


def cache_video_frames(video):
    # cache the video frames for easy sampling later.
    for i in range(the_video_frame_count):
        f = get_frame(video, i)

        # sample the frame and save it in the cache
        for x in range(output_res[0]):
            for y in range(output_res[1]):
                # sample the frame
                frame_size = f.shape
                # print("size: " + str(frame_size))
                frame_x = clamp(int(x * frame_size[1] / output_res[0]), 0, frame_size[1] - 1)
                frame_y = clamp(int(y * frame_size[0] / output_res[1]), 0, frame_size[0] - 1)
                frame_color = f[frame_y, frame_x]

                #print(str(frame_x) + ", " + str(frame_y) + " -> " + str(frame_color))

                # OMG IT'S THE REVERSE ORDER !!!!! B G R instead of R G B. super weird.
                # save in cache
                set_frame_sample(i, x, y, frame_color[2], frame_color[1], frame_color[0])

    print("cached " + str(the_video_frame_count) + " frames into " + str(len(frames_cached)) + " bytes")


cache_video_frames(the_video)



# ########    GUI SETUP 1/2

import PySimpleGUI as sg

layout = [
    [sg.Text("it REAL")],
    #[sg.Button("-")],
    #[sg.Button("+")],
    # the preview image
    [sg.Image(filename="", key="preview_image")],
    # text where we can output the mouse position
    [sg.Text("mouse pos", key="mousepos")],
    [sg.Text("window pos", key="windowpos")],
    [sg.Button("OK")],
]

# Create the window
#window = sg.Window("REAL", layout, finalize=True)
# bind to mouse move event
#window.bind('<Motion>', 'Motion')


# usage:         write_image_to_ui(get_frame(the_video, frame_index))
def write_image_to_ui(frame):
    # convert to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # resize to the output resolution
    frame = cv2.resize(frame, output_res, interpolation=cv2.INTER_AREA)

    # convert to bytes
    imgbytes = cv2.imencode(".png", frame)[1].tobytes()

    # update the image in the UI
    #window["preview_image"].update(data=imgbytes)


# ####### XLED Setup

#from xled_plus.samples.sample_setup import *

# we do our own setup script so we can use the multicontrol rather than the highcontrol
from xled.discover import xdiscover
from xled_plus.multicontrol import MultiHighControlInterface
from xled_plus.ledcolor import *
from xled_plus.pattern import *
from xled_plus.effects import *
from xled_plus.sequence import *
from xled_plus.shapes import *
from sys import argv


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

    return mhci


class HoratiuEffect(Effect):
    def __init__(self, ctr):
        super(HoratiuEffect, self).__init__(ctr)
        self.big_ctr:MultiHighControlInterface = ctr
        self.pat = None

        self.preferred_frames = 1
        self.preferred_fps = FRAMERATE

        self.mouse_xy_01 = (0, 0) # normalized mouse position in window

        self.prev_frame_index = 0

    def reset(self, numframes=False):
        print("ahem : " + type(self.big_ctr).__name__)
        self.pat = self.big_ctr.make_func_pattern(lambda i: rgb_color(1, 0, 0))

    # def launch_rt(self):
    #     global effect_timer
    #
    #     def doit():
    #         # do it for all the ctr not just the one.
    #         self.ctr.show_rt_frame(self.getnext())
    #
    #     if effect_timer:
    #         effect_timer.cancel()
    #     effect_timer = RepeatedTimer(1.0 / self.preferred_fps, doit)
    #     self.reset(False)
    #     effect_timer.start()
    #     return True

    def layout_pattern_uv(self, pos, ind):
        # map the pos to 0..1 and flip y
        pos_01 = (pos[0] + 0.5, 1 - pos[1])

        # if mouse position is equal the current position, return white
        # but put it in a grid tho
        if round(self.mouse_xy_01[0] * output_res[0]) == round(pos_01[0] * output_res[0]) and round(self.mouse_xy_01[1] * output_res[1]) == round(pos_01[1] * output_res[1]):
            return rgb_color(1, 1, 1)

        pos_outline = (0, 0)
        if pos_01[0] <= 1/output_res[0] or pos_01[0] >= (output_res[0] - 1)/output_res[0]:
            return rgb_color(1, 1, 1)
        if pos_01[1] <= 1/output_res[1] or pos_01[1] >= (output_res[1] - 1)/output_res[1]:
            return rgb_color(1, 1, 1)

        # return the UV
        return rgb_color(pos_01[0], pos_01[1], 0)

    def layout_pattern_video(self, pos, ind, frame_index):
        # global the_video

        # map the pos to 0..1 and flip y
        pos_01 = (pos[0] + 0.5, 1 - pos[1])

        x = round(pos_01[0] * output_res[0])
        y = round(pos_01[1] * output_res[1])

        x = clamp(x, 0, output_res[0] - 1)
        y = clamp(y, 0, output_res[1] - 1)

        frame_color = get_frame_sample(frame_index, x, y)

        # return in the twinkly format
        return rgb_color(frame_color[0] / 255, frame_color[1] / 255, frame_color[2] / 255)

    def getnext(self):
        frame_index = int(self.mouse_xy_01[0] * the_video_frame_count)

        # only update on change
        # if self.prev_frame_index == frame_index:
        #     return self.pat
        self.prev_frame_index = frame_index

        # add a sin wobble to the frame index to make it seem more dynamic. PROBLEM: doesn't update fast enough.
        # global sin_time
        # sin_time = 0#sin_time + 1/FRAMERATE * 2 * math.pi
        # frame_offset = int((math.sin(sin_time) * 0.5 + 0.5) * the_video_frame_count * 0.1)
        # final_frame_index = clamp(frame_index + frame_offset, 0, the_video_frame_count - 1)

        # write the image to the UI as well
        write_image_to_ui(get_frame(the_video, frame_index))

        # NOTE: after testing, it seems this function getnext() is being called quite infrequently,
        # so our performance bottleneck might be related to the implementation of getnext() and how it gets called.

        print("WRITE " + str(self.mouse_xy_01))

        self.pat = self.big_ctr.make_layout_pattern(
            lambda pos, ind: self.layout_pattern_video(pos, ind, frame_index)
            # lambda pos, ind: self.layout_pattern_uv(pos, ind)
            , index=True)
        # self.pat = self.big_ctr.make_solid_pattern(rgb_color(0, 1, 1))

        return self.pat


# setup and run the thing, and also shut it down when done
big_ctr = setup_control()
print("Finished setup control...")
big_ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
eff = HoratiuEffect(big_ctr)
oldmode = big_ctr.get_mode()["mode"]
eff.launch_rt()
print("Started continuous effect - press Return to stop it (or close window)")
# input()
# eff.stop_rt()
# big_ctr.set_mode(oldmode)




# ########    GUI SETUP 2/2

def on_press(delta):
    # nothing
    pass

# Create an event loop
# while True:
#     event, values = window.read(timeout=20)
#
#     if event == "Motion":
#         # cursor position in window
#         mouse_pos = window.mouse_location()
#         window_pos = window.current_location()
#         # window size
#         window_size = window.size
#         # normalized mouse position
#         mouse_xy_01 = ((mouse_pos[0] - window_pos[0]) / window_size[0], (mouse_pos[1] - window_pos[1]) / window_size[1])
#         mouse_xy_01 = (clamp(mouse_xy_01[0], 0, 1), clamp(mouse_xy_01[1], 0, 1))
#
#         eff.mouse_xy_01 = mouse_xy_01
#
#         # update mouse position in text UI
#         # position with 2 decimals
#         window["mousepos"].update("mouse pos: " + str(round(mouse_xy_01[0], 2)) + ", " + str(round(mouse_xy_01[1], 2)))
#         window["windowpos"].update("window pos: " + str(window_pos))
#
#
#     # End program if user closes window or
#     # presses the OK button
#     if event == "OK" or event == sg.WIN_CLOSED:
#         break


# make the mouse move around over time
dt = 0
dir = 1
while True:
    dt += 0.05 * dir
    eff.mouse_xy_01 = (clamp(dt, 0, 1), 0)
    if (dt >= 1):
        dir = -1
    elif (dt <= 0):
        dir = 1

    print("M " + str(eff.mouse_xy_01))

    # if there is keyboard input, break the while loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # wait 100 milliseconds
    cv2.waitKey(100)

eff.stop_rt()
big_ctr.set_mode(oldmode)

# window.close()
