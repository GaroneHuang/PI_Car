import wiringpi as wp
import multiprocessing as mt
from motor import Motor
from distance_cal import Distance_Module
from gy271m import GY271M
from maps import Maps
import time
import numpy as np
import os
import cv2
import pyzbar.pyzbar as pyzbar

# define multiprocess information queue
# queue for distance to motor
# queue1 for main to motor
# queue2 for camera to main
# queue3 for distance to camera
# queue4 for motor to camera
queue = mt.Queue(1)
queue1 = mt.Queue(1)
queue2 = mt.Queue(1)
queue3 = mt.Queue(1)
queue4 = mt.Queue(1)

# define map
dist_matrix = [[0, 6, -1, -1, -1, 5, 8],
               [6, 0, 10, -1, -1, -1, -1],
               [-1, 10, 0, 4, -1, -1, 3],
               [-1, -1, 4, 0, 7, -1, -1],
               [-1, -1, 5, 7, 0, 2, 4],
               [5, -1, -1, -1, 2, 0, -1],
               [8, -1, 3, -1, 4, -1, 0]]
dist_matrix = np.array(dist_matrix)
Map = Maps(dist_matrix, dist_matrix)

# define motor
pwm0 = 1
pwm1 = 23
in1 = 29
in2 = 28
in3 = 27
in4 = 26

# Define module pin
dist_head_trig = 2
dist_head_echo = 3
# dist_right_trig = 12
# dist_right_echo = 13
# dist_left_trig = 24
# dist_left_echo = 25
dist_upright_trig = 14
dist_upright_echo = 30
dist_upleft_trig = 21
dist_upleft_echo = 22

device = 0x1e

dist_head = Distance_Module(dist_head_trig, dist_head_echo)
dist_upright = Distance_Module(dist_upright_trig, dist_upright_echo)
dist_upleft = Distance_Module(dist_upleft_trig, dist_upleft_echo)

mag = GY271M(device)

m1 = Motor(pwm0, pwm1, in1, in2, in3, in4)


def Get_Task():
    '''
    没有任务时应阻塞不返回
    返回值为任务ID和到达地点（int）
    不接受参数
    '''
    # TODO Acquiring Tasks
    pass


def Finish_Task():
    '''
    接受参数为任务ID
    返回值自定
    '''
    # TODO Tasks Response
    pass


def Camera():
    cap = cv2.VideoCapture(0)
    distance_data = 15.0
    motor_speed = 0
    while(True):
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 0)
            if queue2.empty():
                queue2.put(frame)
            if not queue3.empty():
                distance_data = queue3.get()
            if not queue4.empty():
                motor_speed = queue4.get()
            # TODO Vedio Transmission
            # return


def Distance_Data():
    print('Distance PID:%i' % os.getpid())
    while(True):
        f = 0
        datas = [0, 0, 0]
        distance_head = dist_head.dist()
        distance_upright = dist_upright.dist()
        distance_upleft = dist_upleft.dist()
        datas[0] = distance_head
        datas[1] = distance_upright
        datas[2] = distance_upleft
        # print(datas)
        for index, item in enumerate(datas):
            if item <= 0.2:
                f = 1
                break
        if queue.empty():
            queue.put(f)
        if queue3.empty():
            queue3.put(datas)
        # time.sleep(0.5)
    return


def Magnet_Data():
    print('Magnet PID:%i' % os.getpid())
    current_target = -1
    speed_left = 768
    speed_right = 768
    flag = 0
    while(True):
        if not queue.empty():
            flag = queue.get()
        if flag == 1:
            # print('Attack!')
            m1.Break()
            if queue4.empty():
                queue4.put(0)
        elif flag == 0:
            if current_target != -1:
                if not queue1.empty():
                    m1.Break()
                    current_target = -1
                    continue
                datas = mag.Get_Data()
                print('Magnet angle:%f' % datas)
                if datas - current_target > 2:  # 偏右
                    speed_left = 0
                    speed_right = 768
                elif current_target - datas > 2:  # 偏左
                    speed_right = 0
                    speed_left = 768
                else:
                    speed_left = speed_right = 768
                m1.Accelerate(speed_left, speed_right)
                if queue4.empty():
                    queue4.put(768)
            elif current_target == -1:
                m1.Accelerate(speed_left, speed_right)
                pass
                # m1.Break()
                # if queue4.empty():
                #     queue4.put(0)
                # while(queue1.empty()):
                #     pass
                # current_target = queue1.get()
                # if current_target == -1:
                #     continue
                # datas = mag.Get_Data()
                # print(datas)
                # while(abs(datas - current_target) > 2):
                #     if queue4.empty():
                #         queue4.put(0)
                #     datas = mag.Get_Data()
                #     print(datas)
                #     m1.Turn(512, 512, 0)
                # m1.Break()


def Get_Init():
    speed = 512
    cap = cv2.VideoCapture(0)
    start = time.time()
    while(True):
        m1.Break()
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 0)
            data, coor = QR_Code(frame)
            if data != None:
                (x, y, w, h) = coor
                if (w < 50) or (h < 50):
                    pass
                else:
                    m1.Drift()
                    cap.release()
                    return data, (x, y, w, h)
            if (time.time() - start < 2):
                continue
            m1.Turn(speed, speed, 0)
            time.sleep(0.3)
            start = time.time()


if __name__ == "__main__":
    print('Main PID:%i' % os.getpid())
    #startpoint = Get_Init()
    p = mt.Pool(3)
    p.apply_async(func=Magnet_Data)
    p.apply_async(func=Distance_Data)
    p.apply_async(func=Camera)
    videowriter = cv2.VideoWriter('test2.avi', cv2.VideoWriter_fourcc(
        'I', '4', '2', '0'), 30, (640, 480))
    flag = 0
    # queue1.put(278)
    while(True):
        try:
            while(True):
                if not queue2.empty():
                    frame = queue2.get()
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    barcodes = pyzbar.decode(gray)
                    if barcodes != None:
                        for barcode in barcodes:
                            (x, y, w, h) = barcode.rect
                            data = barcode.data.decode('utf-8')
                            cv2.rectangle(
                                frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                            if (w < 90) or (h < 90):
                                pass
                            else:
                                print(data)
                                print(w, h)
                                flag = 1
                    videowriter.write(frame)
                    if flag == 1:
                        while(True):
                            m1.Drift()
                pass
                # taskid, endpoint = Get_Task()
                # taskpath = Map.Get_Best(startpoint, endpoint)
                # startpoint = endpoint
                # for i in range(len(taskpath) - 1):
                #     st = taskpath[i]
                #     ed = taskpath[i+1]
                #     path_mag = Map.mag_matrix[st, ed]
                #     while(queue1.full()):
                #         # m1.Break()
                #         pass
                #     queue1.put(path_mag)
                #     while(queue1.full()):
                #         pass
                #     while(True):
                #         if not queue2.empty():
                #             frame = queue2.get()
                #             data, coor = QR_Code(frame)
                #             if data != -1:
                #                 (x, y, w, h) = coor
                #                 data = int(data)
                #                 if (w < 50) or (h < 50):
                #                     pass
                #                 elif data == ed:
                #                     queue1.put(-1)
                #                     break
                # Finish_Task()
        except KeyboardInterrupt:
            p.close()
            p.terminate()
            m1.Drift()
            break
