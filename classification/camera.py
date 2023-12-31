from imutils.video import VideoStream
import imutils
import cv2,os,urllib.request
import numpy as np
from django.conf import settings

#Laptop Camera
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    #This function is used in views
    def get_frame(self):

        success, image = self.video.read()
        frame_flip = cv2.flip(image, 1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()


#ESP32 Cam
class IPWebCam(object):
    def __init__(self):
        self.url = "http://192.168.0.100:8080/shot.jpg"

    def __del__(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        imgResp = urllib.request.urlopen(self.url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        img =cv2.resize(img, (640, 480))
        frame_flip = cv2.flip(img, 1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()