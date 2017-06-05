"""
 To control the pixel ring of the ReSpeaker microphone array
 Copyright (c) 2016-2017 Seeed Technology Limited.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import usb.core
import usb.util


class HID:
    """
    This class provides basic functions to access
    a USB HID device to write an endpoint
    """

    def __init__(self):
        self.dev = None
        self.ep_in = None
        self.ep_out = None

    @staticmethod
    def find(vid=0x2886, pid=0x0007):
        dev = usb.core.find(idVendor=vid, idProduct=pid)
        if not dev:
            return

        # get active config
        config = dev.get_active_configuration()

        # iterate on all interfaces:
        #    - if we found a HID interface
        interface_number = None
        for interface in config:
            if interface.bInterfaceClass == 0x03:
                interface_number = interface.bInterfaceNumber
                break

        try:
            if dev.is_kernel_driver_active(interface_number):
                dev.detach_kernel_driver(interface_number)
        except Exception as e:
            print(e.message)

        ep_in, ep_out = None, None
        for ep in interface:
            if ep.bEndpointAddress & 0x80:
                ep_in = ep
            else:
                ep_out = ep

        if ep_in and ep_out:
            hid = HID()
            hid.dev = dev
            hid.ep_in = ep_in
            hid.ep_out = ep_out

            return hid

    def write(self, data):
        """
        write data on the OUT endpoint associated to the HID interface
        """
        self.ep_out.write(data)

    def read(self):
        return self.ep_in.read(self.ep_in.wMaxPacketSize, -1)

    def close(self):
        """
        close the interface
        """
        usb.util.dispose_resources(self.dev)


class PixelRing:
    PIXELS_N = 12

    MONO = 1
    SPIN = 3
    ARC  = 5
    CUSTOM = 6

    def __init__(self):
        self.hid = HID.find()
        if not self.hid:
            print('No USB device found')

        colors = [0] * 4 * self.PIXELS_N
        colors[0] = 0x4
        colors[1] = 0x40
        colors[2] = 0x4

        colors[4 + 1] = 0x8
        colors[4 * 11 + 1] = 0x8

        self.direction_template = colors

    def off(self):
        self.set_color(rgb=0)

    def set_color(self, rgb=None, r=0, g=0, b=0):
        if rgb:
            self.write(0, [self.MONO, rgb & 0xFF, (rgb >> 8) & 0xFF, (rgb >> 16) & 0xFF])
        else:
            self.write(0, [self.MONO, b, g, r])

    def spin(self):
        self.write(0, [self.SPIN, 0, 0, 0])

    def arc(self, pixels):
        self.write(0, [self.ARC, 0, 0, pixels])

    def set_direction(self, angel):
        if angel < 0 or angel > 360:
            return

        position = int((angel + 15) % 360 / 30) % self.PIXELS_N
        colors = self.direction_template[-position*4:] + self.direction_template[:-position*4]

        self.write(0, [self.CUSTOM, 0, 0, 0])
        self.write(3, colors)

        return position

    @staticmethod
    def to_bytearray(data):
        if type(data) is int:
            array = bytearray([data & 0xFF])
        elif type(data) is bytearray:
            array = data
        elif type(data) is str or type(data) is bytes:
            array = bytearray(data)
        elif type(data) is list:
            array = bytearray(data)
        else:
            raise TypeError('%s is not supported' % type(data))

        return array

    def write(self, address, data):
        data = self.to_bytearray(data)
        length = len(data)
        if self.hid:
            packet = bytearray([address & 0xFF, (address >> 8) & 0xFF, length & 0xFF, (length >> 8) & 0xFF]) + data
            self.hid.write(packet)

    def close(self):
        if self.hid:
            self.hid.close()


pixel_ring = PixelRing()


if __name__ == '__main__':
    import time

    pixel_ring.spin()
    time.sleep(3)
    for level in range(4, 8):
        pixel_ring.arc(level)
        time.sleep(1)

    angel = 0
    while True:
        try:
            pixel_ring.set_direction(angel)
            angel = (angel + 30) % 360
            time.sleep(1)
        except KeyboardInterrupt:
            break

    pixel_ring.off()
