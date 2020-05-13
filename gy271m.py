import os
import wiringpi as wp
import time
import math


class GY271M(object):
    def __init__(self, device_add):
        self.device = device_add
        self.read_start_address = 0x03
        self.register_A = 0x00
        self.register_B = 0x01
        self.register_Mode = 0x02
        self.mag_off = 3.2
        self.SetUp()
        return

    def SetUp(self):
        wp.wiringPiSetup()
        self.fd = wp.wiringPiI2CSetup(self.device)
        wp.wiringPiI2CWriteReg8(self.fd, self.register_A, 0x70)
        wp.wiringPiI2CWriteReg8(self.fd, self.register_B, 0x20)
        wp.wiringPiI2CWriteReg8(self.fd, self.register_Mode, 0x00)
        # self.CalibrateMag(self.fd)
        return

    def Read_Data(self, fd):
        x_msb = wp.wiringPiI2CReadReg8(self.fd, self.read_start_address)
        x_lsb = wp.wiringPiI2CReadReg8(self.fd, self.read_start_address+1)
        z_msb = wp.wiringPiI2CReadReg8(self.fd, self.read_start_address+2)
        z_lsb = wp.wiringPiI2CReadReg8(self.fd, self.read_start_address+3)
        y_msb = wp.wiringPiI2CReadReg8(self.fd, self.read_start_address+4)
        y_lsb = wp.wiringPiI2CReadReg8(self.fd, self.read_start_address+5)
        X = x_msb*256+x_lsb
        Y = y_msb*256+y_lsb
        Z = z_msb*256+z_lsb
        X = X - 65536 if X > 32768 else X
        Y = Y - 65536 if Y > 32768 else Y
        Z = Z - 65536 if Z > 32768 else Z
        return X, Y, Z

    def CalibrateMag(self, fd):
        x, y, z = self.Read_Data(fd)
        xmax = xmin = x
        ymax = ymin = y
        zmax = zmin = z
        print("开始校准罗盘...............")
        print("请把罗盘在40秒内空间翻转360度")
        for i in range(4000):
            x, y, z = self.Read_Data(fd)
            if x > xmax:
                xmax = x
            if x < xmin:
                xmin = x
            if y > ymax:
                ymax = y
            if y < ymin:
                ymin = y
            if z > zmax:
                zmax = z
            if z < zmin:
                zmin = z
            time.sleep(0.01)
            if i % 100 == 0:
                print('Xmax:%f' % xmax)
                print('Ymax:%f' % ymax)
                print('Zmax:%f' % zmax)
        self.x_off = int((xmax + xmin) / 2)
        self.y_off = int((ymax + ymin) / 2)
        self.z_off = int((zmax + zmin) / 2)
        return

    def CalAngles(self, x, y, z):
        #radians = math.atan2(y-self.y_off, x-self.x_off)
        radians = math.atan2(y, x) + math.pi
        # if radians < 0:
        #     radians += 2*math.pi
        # elif radians > 2*math.pi:
        #     radians -= 2*math.pi
        angle = radians * 180.0 / math.pi
        return angle

    def Get_Data(self):
        x, y, z = self.Read_Data(self.fd)
        # print('X:%f' % x)
        # print('Y:%f' % y)
        # print('Z:%f' % z)
        angle = self.CalAngles(x, y, z)
        return angle


if __name__ == "__main__":
    device = 0x1e
    mag = GY271M(device)
    while(True):
        angle = mag.Get_Data()
        print('Angle:%f' % angle)
        time.sleep(0.2)
