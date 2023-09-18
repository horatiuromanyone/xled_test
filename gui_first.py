"""
I'm using a GUI library called PySimpleGUI to make a simple GUI.
then I make 2 buttons that let you change which movie is being displayed.
the movies must be loaded by phone into the device first, and the total movie amount is hardcoded to 5.
NOTE: this uses the vanilla xled package, not the xled-plus
"""

import xled
import PySimpleGUI as sg

layout = [
    [sg.Text("Color picker lol")],
    [sg.Button("-")],
    [sg.Button("+")],
    [sg.Button("OK")],
]

# Create the window
window = sg.Window("Demo", layout)


# xled stuff
discovered_device = xled.discover.discover()
control_high = xled.HighControlInterface(discovered_device.ip_address, discovered_device.hw_address)
control = xled.ControlInterface(discovered_device.ip_address, discovered_device.hw_address)
frame_index = 0
num_frames = 5
control_high.turn_on()
control_high.set_mode('movie')


# we can redo this in case we lose connection for some reason
def init_device():
    discovered_device = xled.discover.discover()
    control_high = xled.HighControlInterface(discovered_device.ip_address, discovered_device.hw_address)
    control = xled.ControlInterface(discovered_device.ip_address, discovered_device.hw_address)

    if not control_high.is_on():
        control_high.turn_on()

    if not control_high.get_mode()['mode'] == 'movie':
        control_high.set_mode('movie')


def OnPress(delta):

    if (discovered_device is None):
        print("rediscovering device...")
        init_device()

    # set the frame to frame+delta
    global frame_index
    frame_index = (frame_index + delta) % num_frames
    control_high.set_movies_current(frame_index)






# Create an event loop
while True:
    event, values = window.read()

    if event == "-":
        OnPress(-1)
    elif event == "+":
        OnPress(1)

    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()