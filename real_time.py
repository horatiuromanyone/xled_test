"""
inspired from: xled_plus/samples/day29.py

start a realtime mode and send colors each frame.
found a way to set color based on the LED coordinate. it wasn't easy.

"""
import io
import math

#from xled_plus.samples.sample_setup import *

# we do our own setup script so we can use the multicontrol rather than the highcontrol
import sys
import time

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


if sys.version_info.major == 2:
    from threading import _Timer

    TimerX = _Timer
else:
    from threading import Timer

    TimerX = Timer


effect_timer = None


class RepeatedTimer(TimerX):
    def run(self):
        lasttime = time.time()
        self.function(*self.args, **self.kwargs)
        while not self.finished.wait(
            max(0.0, self.interval - (time.time() - lasttime))
        ):
            lasttime = time.time()
            self.function(*self.args, **self.kwargs)


class HoratiuEffect(Effect):
    def __init__(self, ctr):
        super(HoratiuEffect, self).__init__(ctr)
        self.pat = None

        self.preferred_frames = 30
        self.preferred_fps = 16

    def reset(self, numframes=False):
        self.pat = self.ctr.make_func_pattern(lambda i: rgb_color(0, 0, 0))

    def launch_rt(self):
        print("launch RTTTTTTTT!!!!!!!!!!!!!!!")
        global effect_timer

        def doit():
            print("Doing it")
            self.ctr.show_rt_frame(self.getnext())

        if effect_timer:
            effect_timer.cancel()
        effect_timer = RepeatedTimer(1.0 / self.preferred_fps, doit)
        self.reset(False)
        effect_timer.start()
        return True

    def getnext(self):
        print("num: " + str(ctr.num_leds))
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