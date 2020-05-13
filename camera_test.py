import cv2
import socket
import numpy as np
import math

cap = cv2.VideoCapture(0)
#width, height = 640, 480

address = ("192.168.1.3", 8000)
tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


tcpClientSocket.connect(address)
pkg_size = 512

begin_msg = b"CameraBgn"
middle_msg = b"CameraMid"
end_msg = b"CameraEnd"

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 0)
    if ret:
        _, jpg_data = cv2.imencode(".jpg", frame)
        pkg_num = math.ceil(jpg_data.shape[0]/pkg_size)
        temp = np.array([pkg_num, jpg_data.shape[0]-pkg_size *
                         (pkg_num-1)], dtype=np.uint16).tostring()
        data = begin_msg+temp
        tcpClientSocket.send(data)
        for i in range(pkg_num-1):
            data = middle_msg+jpg_data[pkg_size*i:pkg_size*(i+1)].tostring()
            tcpClientSocket.send(data)
        data = end_msg+jpg_data[pkg_size *
                                (pkg_num-1):jpg_data.shape[0]].tostring()
        tcpClientSocket.send(data)
