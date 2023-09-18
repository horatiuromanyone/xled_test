"""
inspired from: xled_plus/samples/day29.py

start a realtime mode and send colors each frame.
found a way to set color based on the LED coordinate. it wasn't easy.

"""
import io
import math

from xled_plus.samples.sample_setup import *

class HoratiuEffect(Effect):
    def __init__(self, ctr):
        super(HoratiuEffect, self).__init__(ctr)
        self.pat = None

        self.preferred_frames = 2
        self.preferred_fps = 12

    def reset(self, numframes=False):
        self.pat = self.ctr.make_func_pattern(lambda i: rgb_color(0, 0, 0))

    def getnext(self):
        #print("num: " + str(ctr.num_leds))
        # make a pattern the dumb way
        new_pattern = ctr.copy_pattern(self.pat)
        ctr.make_solid_pattern(rgb_color(0, 0, 0))
        if False:
            for x in range(0, 16):
                for y in range(0, 16):
                    ctr.modify_pattern(new_pattern, x*16 + y, rgb_color(x, y, 0))

        new_la_pattern = ctr.make_layout_pattern(lambda pos, ind:
                     rgb_color(pos[0], pos[1], -pos[0])

                     , index=True)
        self.pat = new_la_pattern

        return self.pat


ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
eff = HoratiuEffect(ctr)
oldmode = ctr.get_mode()["mode"]
eff.launch_rt()
print("Started continuous effect - press Return to stop it")
input()
eff.stop_rt()
ctr.set_mode(oldmode)