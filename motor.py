import wiringpi as wp
import os


class Motor(object):
    def __init__(self, ena, enb, in1, in2, in3, in4):
        super(Motor, self).__init__()
        self.pwm0 = ena
        self.pwm1 = enb
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.side = (0, 1, 1, 0)
        self.Setup()
        return

    def Setup(self):
        wp.wiringPiSetup()
        wp.pinMode(self.pwm0, wp.PWM_OUTPUT)
        wp.pinMode(self.pwm1, wp.PWM_OUTPUT)
        wp.pinMode(self.in1, wp.OUTPUT)
        wp.pinMode(self.in2, wp.OUTPUT)
        wp.pinMode(self.in3, wp.OUTPUT)
        wp.pinMode(self.in4, wp.OUTPUT)
        return

    def Write4Pin(self, side):
        wp.digitalWrite(self.in1, side[0])
        wp.digitalWrite(self.in2, side[1])
        wp.digitalWrite(self.in3, side[2])
        wp.digitalWrite(self.in4, side[3])

    def Drift(self):
        wp.pwmWrite(self.pwm0, 0)
        wp.pwmWrite(self.pwm1, 0)
        self.Write4Pin((0, 0, 0, 0))
        return

    def Accelerate(self, num0, num1):
        # num / 1024
        wp.pwmWrite(self.pwm0, num0)
        wp.pwmWrite(self.pwm1, num1)
        self.Write4Pin(self.side)
        return

    def Turn(self, num_left, num_right, right):
        # num0 for right side
        # num1 for left side
        wp.pwmWrite(self.pwm0, num_right)
        wp.pwmWrite(self.pwm1, num_left)
        if right == 0:
            self.Write4Pin((1, 0, 1, 0))
        else:
            self.Write4Pin((0, 1, 0, 1))
        return

    def Break(self):
        wp.pwmWrite(self.pwm0, 1024)
        wp.pwmWrite(self.pwm1, 1024)
        self.Write4Pin((1, 1, 1, 1))
        return

    def TurnAround(self):
        if self.side == (0, 1, 1, 0):
            self.side = (1, 0, 0, 1)
        elif self.side == (1, 0, 0, 1):
            self.side = (0, 1, 1, 0)
        return
