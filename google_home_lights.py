#!/usr/bin/env python

# Copyright (C) 2017 Seeed Technology Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pixel_ring import pixel_ring
import numpy
import time
import threading
try:
    import queue as Queue
except ImportError:
    import Queue as Queue


class GoogleHomeLights:
    def __init__(self):
        self.basis = numpy.array([0] * 4 * 12)
        self.basis[0 * 4 + 0] = 2
        self.basis[3 * 4 + 2] = 2
        self.basis[6 * 4 + 1] = 1
        self.basis[6 * 4 + 2] = 1
        self.basis[9 * 4 + 1] = 2

        self.pixels = self.basis * 0
        self.write(self.pixels)

        pixel_ring.write(0, [6, 0, 0, 0])

        self.next = threading.Event()
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def wakeup(self, direction=0):
        def f():
            self._wakeup(direction)
        self.queue.put(f)

    def listen(self):
        self.next.set()
        self.queue.put(self._listen)

    def think(self):
        self.next.set()
        self.queue.put(self._think)

    def speak(self):
        self.next.set()
        self.queue.put(self._speak)

    def off(self):
        self.next.set()
        self.queue.put(self._off)


    def _run(self):
        while True:
            func = self.queue.get()
            func()

    def _wakeup(self, direction=0):
        position = int((direction + 15) / 30) % 12

        basis = numpy.roll(self.basis, position * 4)
        for i in range(1, 25):
            pixels = basis * i
            self.write(pixels)
            time.sleep(0.005)

        pixels =  numpy.roll(pixels, 4)
        self.write(pixels)
        time.sleep(0.1)

        for i in range(2):
            new_pixels = numpy.roll(pixels, 4)
            self.write(new_pixels * 0.5 + pixels)
            pixels = new_pixels
            time.sleep(0.1)

        self.write(pixels)
        self.pixels = pixels

    def _listen(self):
        pixels = self.pixels
        for i in range(1, 25):
            self.write(pixels * i / 24)
            time.sleep(0.01)

    def _think(self):
        pixels = self.pixels

        self.next.clear()
        while not self.next.is_set():
            pixels = numpy.roll(pixels, 4)
            self.write(pixels)
            time.sleep(0.2)

        t = 0.1
        for i in range(0, 5):
            pixels = numpy.roll(pixels, 4)
            self.write(pixels * (4 - i) / 4)
            time.sleep(t)
            t /= 2

        # time.sleep(0.5)

        self.pixels = pixels

    def _speak(self):
        pixels = self.pixels

        self.next.clear()
        while not self.next.is_set():
            for i in range(5, 25):
                self.write(pixels * i / 24)
                time.sleep(0.01)

            time.sleep(0.3)

            for i in range(24, 4, -1):
                self.write(pixels * i / 24)
                time.sleep(0.01)

            time.sleep(0.3)

        self._off()

    def _off(self):
        self.write([0] * 4 * 12)

    def write(self, data):
        if type(data) is list:
            pixel_ring.write(3, data)
        else:
            pixel_ring.write(3, data.astype('uint8').tostring())


lights = GoogleHomeLights()


if __name__ == '__main__':
    while True:

        try:
            lights.wakeup()
            time.sleep(3)
            lights.think()
            time.sleep(3)
            lights.speak()
            time.sleep(3)
            lights.off()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixel_ring.off()