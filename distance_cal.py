import os
import wiringpi as wp
import time


class Distance_Module(object):
    def __init__(self, pin_trig, pin_echo):
        self.pin_trig = pin_trig
        self.pin_echo = pin_echo
        wp.wiringPiSetup()
        wp.pinMode(self.pin_trig, wp.OUTPUT)
        wp.pinMode(self.pin_echo, wp.INPUT)

    def dist(self):
        wp.digitalWrite(self.pin_trig, wp.LOW)
        wp.digitalWrite(self.pin_trig, wp.HIGH)
        time.sleep(0.000015)
        wp.digitalWrite(self.pin_trig, wp.LOW)
        t0 = time.time()
        while(wp.digitalRead(self.pin_echo) == wp.LOW):
            if time.time() - t0 > 0.08:
                return -1.0
            pass
        t1 = time.time()
        while((wp.digitalRead(self.pin_echo) == wp.HIGH)):
            # if time.time() - t1 > 0.008:
            #     return -1.0
            pass
        t2 = time.time()
        minors = t2-t1
        distance = minors*340.0/2
        return distance


# pin_trig = 24
# pin_echo = 25
# d1 = Distance_Module(pin_trig=pin_trig, pin_echo=pin_echo)
# while(True):
#     distance = d1.dist()
#     if distance == -1.0:
#         print('Too Far Away!')
#     else:
#         print('Distance:%0.2f m' % distance)
#     time.sleep(0.5)
