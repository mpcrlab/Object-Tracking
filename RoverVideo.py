from time import sleep
from rover import Rover20
#from RoverControl import *
import cv2, numpy as np, pygame


class Rover(Rover20):
    def __init__(self):
        Rover20.__init__(self)
        print self.get_battery_percentage()
        #self.rover = Rover20()
        pygame.init()
        #self.file_name = 'filename'
        self.quit = False
        self.image = None
        self.run()
        self.close()


    def run(self):
        sleep(1.5)
        while not self.quit:
            self.process_video_from_rover()
        self.quit = True
        pygame.quit()

    def TO(self):
             # Take each frame
            frame = self.image

            imgHeight,imgWidth, imgChannels = frame.shape
            # Convert BGR to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            cv2.imshow("hsv", hsv)

            # define range of each color in HSV
            lower_orange = np.array([153,70,168])
            upper_orange = np.array([140,256,256])

            lower_pink = np.array([147,95,150])
            upper_pink = np.array([227,255,255])


            # Threshold the HSV image to get only colors we want
            Omask = cv2.inRange(hsv, lower_orange, upper_orange)
            Pmask = cv2.inRange(hsv, lower_pink,upper_pink)
            # Bitwise-AND mask and original image to show thresholded images with the correct colors
            Ores = cv2.bitwise_and(frame,frame, mask= Omask)
            Pres = cv2.bitwise_and(frame,frame,mask = Pmask)

            #show the result with no noise filtering
            cv2.imshow('Pmask1',Pres)

            #Seed the kernel, any (x,x) collection of pixels that is not completely filled will be filtered out
            kernel = np.ones((5,5),np.uint8)
            # Use kernel to implement the Open and Close morphological expressions

            Pres = cv2.morphologyEx(Pres, cv2.MORPH_OPEN, kernel)
            Pres = cv2.morphologyEx(Pres, cv2.MORPH_CLOSE, kernel)

            cv2.imshow('0mask1',Pres)

            kernel = np.ones((9,9),np.uint8)
            Ores = cv2.morphologyEx(Ores, cv2.MORPH_CLOSE, kernel)

            Ores = cv2.morphologyEx(Ores, cv2.MORPH_OPEN, kernel)


            #convert the noise filetered image back to hsv
            hsvPres = cv2.cvtColor(Pres, cv2.COLOR_BGR2HSV)
            hsvOres = cv2.cvtColor(Ores, cv2.COLOR_BGR2HSV)


            #Create a new mask with the noise filtered image
            Pmask2 = cv2.inRange(hsvPres, lower_pink,upper_pink)
            Omask2 = cv2.inRange(hsvOres,lower_orange,upper_orange)

            # Create image with just colors that we want
            # Note: this is not useful for anything other than just showing the image because
            # the colors are not broken into useful classifications
            rres = cv2.bitwise_or(Ores,Pres)


            # Create of copy of each video frame, all text and colors will go over
            # this image to produce the final result
            img = frame


            # Create an image with the noise filtered mask
            Pimage = Pmask2
            Oimage = Omask2
            # Find the contours of the masked image
            Pimage, Pcontours, Phierarchy = cv2.findContours(Pimage,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
            Oimage, Ocontours, Ohierarchy = cv2.findContours(Oimage,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

            if len(Pcontours) != 0:

                #Find the moments of the first contour
                cnt = []
                M = []
                highestArea = 0
                for i in range(len(Pcontours)):
                    cnt.append(Pcontours[i])
                    M.append(cv2.moments(cnt[i]))
                    cntArea = cv2.contourArea(cnt[i])
                    if cntArea > highestArea:
                        highestArea = cntArea
                        biggestCnt = i
                # Use the moments to find the center x and center y
                cx = int(M[biggestCnt]['m10']/M[biggestCnt]['m00'])
                cy = int(M[biggestCnt]['m01']/M[biggestCnt]['m00'])

                #Convert cx and cx to strings for output
                scx = str(cx)
                scy = str(cy)
                location = "( " + scx + ", " + scy + ")"

                # put text onto the final image at the center of the contour
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img,location,(cx,cy), font, .5,(255,255,255),2,cv2.LINE_AA)

                #Change contour outline to Red if the center is outside the middle third
                # Or green if it is inside the middle third
                if cx <= imgWidth / 3:
                    contourColor = ((0,0,255))
                    self.set_wheel_treads(0,1)
                elif cx > imgWidth / 3 and cx <= 2 * imgWidth / 3:
                    contourColor = ((0,255,0))
                    self.set_wheel_treads(1,1)
                else:
                    contourColor = ((0,0,255))
                    self.set_wheel_treads(1,0)

                    #Draw contours onto the final image
                img = cv2.drawContours(img, Pcontours[i], -1, contourColor, 3)

                    #Draw center point
                img = cv2.circle(img,(cx,cy), 5, (255,0,0), -1)

            else:
                self.set_wheel_treads(0,0)


            #Orange is not up to date so I disabled it
            if len(Ocontours) == -1 :
                 #Find the moments of the first contour
                cnt = []
                M = []
                for i in range(len(Ocontours)):
                    cnt.append(Ocontours[i])
                    M.append(cv2.moments(cnt[i]))
                # Use the moments to find the center x and center y
                    try:
                        cx = int(M[i]['m10']/M[i]['m00'])
                        cy = int(M[i]['m01']/M[i]['m00'])

                    except:
                        print "Too many orange objects"
                #Convert cx and cx to strings for output
                    scx = str(cx)
                    scy = str(cy)
                    location = "( " + scx + ", " + scy + ")"

                # put text onto the final image at the center of the contour
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img,location,(cx,cy), font, .5,(255,255,255),2,cv2.LINE_AA)

                    contourColor = ((0,0,255))

                    #Draw contours onto the final image
                    img = cv2.drawContours(img, Ocontours[i], -1, contourColor, 3)

                    #Draw center point
                    img = cv2.circle(img,(cx,cy), 5, (255,0,0), -1)

                    #self.rover.setTreads(1,0)




            #Break the screen into thirds
            img = cv2.line(img,(imgWidth/3,0),(imgWidth/3,511),(255,0,0),5)
            img = cv2.line(img,(2*imgWidth/3,0),(2*imgWidth/3,511),(255,0,0),5)



            cv2.imshow('Tracking Results',img)
            #cv2.imshow('Camera HSV',hsv)
            #cv2.imshow('Orange Mask',Omask2)
            #cv2.imshow('Pink Mask',Pres)
            #cv2.imshow('Mixed Mask',rres)


            # End program if esc is pressed or show moments and
            # Number of contours is 's' is pressed
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                self.close()
            elif k == 115:
                self.set_wheel_treads(0,0)


    def process_video_from_rover(self, jpegbytes, timestamp_10msec):
        #try:
            #sleep(.5)
            window_name = 'Machine Perception and Cognitive Robotics'
            array_of_bytes = np.fromstring(jpegbytes, np.uint8)
            self.image = cv2.imdecode(array_of_bytes, flags=3)
             # waitkey cannot be zero
            #cv2.waitKey(30)
            self.TO()
        #except:
           # print("Could not find OpenCV")

