import cv2
import numpy as np
import imutils
from shape_detector import *
from project.applications.exam.controller.custom_exceptions.answerAreaROIException import AnswerAreaROIException

class AnswerSheet:
    def __init__(self, sheetPath):
        self.sheet = cv2.imread(sheetPath)
        self.grayScale = self.getGrayScaleImage()
        _, self.binarized = self.getBinarizedSheet(self.grayScale, 125, 255)

    '''
    @:return returns the gray scale converted of the original image
    '''
    def getGrayScaleImage(self):
        self.grayScale = cv2.cvtColor(self.sheet, cv2.COLOR_BGR2GRAY)
        return self.grayScale

    '''
    @:return thresholded image
    '''
    def getBinarizedSheet(self,image, thresh, maxValue):
        ret, self.binarized = cv2.threshold(image, thresh, maxValue, cv2.THRESH_BINARY)
        return ret, self.binarized

    '''
    @:return warped of the image
    '''
    def warpTransformSheet(self):
        rows, cols, ch = self.sheet.shape
        # TODO : do the rest of the job here

    '''
    @:return resited image to give x and y
    '''
    @staticmethod
    def resizeImage(image, x, y):
        image = cv2.resize(image, (x, y))
        return image

    def detect_circles(self, gray):
        gray_blur = cv2.medianBlur(gray, 13)  # Remove noise before laplacian
        gray_lap = cv2.Laplacian(gray_blur, cv2.CV_8UC1, ksize=5)
        dilate_lap = cv2.dilate(gray_lap,
                                (3, 3))  # Fill in gaps from blurring. This helps to detect circles with broken edges.
        # Furture remove noise introduced by laplacian. This removes false pos in space between the two groups of circles.
        lap_blur = cv2.bilateralFilter(dilate_lap, 5, 9, 9)
        # Fix the resolution to 16. This helps it find more circles. Also, set distance between circles to 55 by measuring dist in image.
        # Minimum radius and max radius are also set by examining the image.
        circles = cv2.HoughCircles(lap_blur, cv2.cv.CV_HOUGH_GRADIENT, 16, 55, param2=450, minRadius=20, maxRadius=40)
        # There are some false positives left in the regions containing the numbers.
        # They can be filtered out based on their y-coordinates if your images are aligned to a canonical axis.
        # I'll leave that to you.
        return circles
    '''
    NOTE: change the sensitivity Here

    @:return warped BGR image of the answer Area
    '''
    def findAnswerArea(self, HCirclesParam1 = 30, HCirclesParam2 = 15, mIndicatorCirclesRadius = 7, MIndicatorCirclesRadius = 25):
        img = cv2.medianBlur(self.grayScale,5)

        # img = cv2.Laplacian(img, cv2.CV_8UC1, ksize=5)
        # img = cv2.dilate(img, (9,9))
        # img = cv2.erode(img, (13,13))
        img = cv2.bilateralFilter(img, 10, 9, 9)

        circles = cv2.HoughCircles(img, cv2.cv.CV_HOUGH_GRADIENT, 1, 20, param1=HCirclesParam1, param2=HCirclesParam2, minRadius=mIndicatorCirclesRadius, maxRadius=MIndicatorCirclesRadius)
        circles = np.uint16(np.around(circles))
        points = circles[0]
        pts = np.array([[points[0][0], points[0][1]], [points[1][0], points[1][1]],[points[2][0], points[2][1]], [points[3][0], points[3][1]]], dtype="float32")
        image = self.sheet.copy()
        rect = np.zeros((4, 2), dtype="float32")
        # cv2.imshow("imshow", img)
        # the top-left point has the smallest sum whereas the
        # bottom-right has the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # compute the difference between the points -- the top-right
        # will have the minumum difference and the bottom-left will
        # have the maximum difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # multiply the rectangle by the original ratio
        ratio = image.shape[0] / image.shape[1]
        rect *= ratio

        tl, tr, br, bl = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))

        # ...and now for the height of our new image
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

        # take the maximum of the width and height values to reach
        # our final dimensions
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))

        # construct our destination points which will be used to
        # map the screen to a top-down, "birds eye" view
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # calculate the perspective transform matrix and warp
        # the perspective to grab the screen
        M = cv2.getPerspectiveTransform(rect, dst)
        warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        sd = Shape_detector()
        # compute the center of the contour, then detect the name of the
        # shape using only the contour
        M = cv2.moments(rect)
        cX = int((M["m10"] / M["m00"]) * ratio)
        cY = int((M["m01"] / M["m00"]) * ratio)
        shape = sd.detect(rect)
        # print rect
        pts1X = rect[0, 0]
        pts2X = rect[1 , 0]
        pts3X = rect[2, 0]
        pts4X =  rect[3, 0]
        top_line_len = pts2X - pts1X
        bottom_line_len = pts3X - pts4X

        pts1Y = rect[0, 1]
        pts2Y = rect[1 , 1]
        pts3Y = rect[2, 1]
        pts4Y =  rect[3, 1]
        left_line_len = pts4Y - pts1Y
        right_line_len = pts3Y - pts2Y
        # print right_line_len - left_line_len
        # print top_line_len - bottom_line_len
        # print shape
        error_detection_condition = shape != "square" and shape != "rectangle" and len(rect) == 4
        if error_detection_condition or abs(top_line_len - bottom_line_len) > 20 or abs(left_line_len - right_line_len) > 20:
            raise AnswerAreaROIException("could not find the answer Area")
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = rect.astype("float")
        c *= ratio
        c = rect.astype("int")
        cv2.drawContours(image, [c], -1, (0, 255, 255), 2)
        # show the output image
        # cv2.imwrite("test.jpg", image)
        # cv2.imshow("Image", image)
        # cv2.waitKey()
        # cv2.imshw("test", warp)
        # cv2.waitKey()
        return warp


    # def findAnswerArea(self, HCirclesParam1 = 30, HCirclesParam2 = 15, mIndicatorCirclesRadius = 1, MIndicatorCirclesRadius = 25):
    #     retval, image = cv2.threshold(self.grayScale, 50, 255, cv2.cv.CV_THRESH_BINARY)
    #
    #     el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    #     image = cv2.dilate(image, el, iterations=6)
    #
    #     # cv2.imwrite("dilated.png", image)
    #
    #     contours, hierarchy = cv2.findContours(
    #         image,
    #         cv2.cv.CV_RETR_LIST,
    #         cv2.cv.CV_CHAIN_APPROX_SIMPLE
    #     )
    #
    #     # drawing = cv2.imread("test.jpg")
    #
    #     centers = []
    #     radii = []
    #     for contour in contours:
    #         area = cv2.contourArea(contour)
    #
    #         # there is one contour that contains all others, filter it out
    #         if area > 500:
    #             continue
    #
    #         br = cv2.boundingRect(contour)
    #         radii.append(br[2])
    #
    #         m = cv2.moments(contour)
    #         center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
    #         centers.append(center)
    #
    #     print("There are {} circles".format(len(centers)))
    #
    #     radius = int(np.average(radii)) + 5
    #
    #     # for center in centers:
    #     #     cv2.circle(drawing, center, 3, (255, 0, 0), -1)
    #     #     cv2.circle(drawing, center, radius, (0, 255, 0), 1)
    #
    #     # cv2.imwrite("drawing.png", drawing)





    '''
        divide the answer area to 320 rows and each row divided to 4 columns
        @:return list of bubbles of each row
    '''
    def getAllCells(self, sheetArea, resizeY = 1048, resizeX=904, n_of_choices = 4, n_of_rows = 50):

        sheetArea = cv2.resize(sheetArea, (resizeY,resizeX))
        gray = cv2.cvtColor(sheetArea, cv2.COLOR_BGR2GRAY)
        box1 = gray[55:880, 60:155]
        box2 = gray[55:880, 205:300]
        box3 = gray[55:880, 348:440]
        box4 = gray[55:880, 490:585]
        box5 = gray[58:880, 630:730]
        box6 = gray[55:880, 773:870]
        box7 = gray[55:880, 915:1015]
        # cv2.imshow("bo", box5)
        # cv2.waitKey()
        # box8 = gray[30:905, 920:1020]
        boxes = [box1, box2, box3, box4, box5, box6, box7]
        width = n_of_choices
        height = n_of_rows
        answers = list()


        for i in range(0, 7):
            displacement = 0
            row_counter = 0

            for row in xrange(0, height):
                tmp = list()
                row_counter += 1

                for column in range(width):
                    box = boxes[i]
                    y1 = row * 15 + displacement
                    y2 = y1 + 15
                    x1 = column * 23
                    x2 = x1 + 27
                    tmp += [box[int(y1):int(y2), x1:x2]]
                if row_counter == 10:
                    row_counter = 0
                    displacement += 8
                displacement += 0.5
                answers += [tmp]

        # for i in range(1 ,len(answers) + 1):
        #     cv2.imwrite("./cells/" + str(i) + "a.jpg", answers[i-1][0])
        #     cv2.imwrite("./cells/" +str(i) + "b.jpg", answers[i-1][1])
        #     cv2.imwrite("./cells/" +str(i) + "c.jpg", answers[i-1][2])
        #     cv2.imwrite("./cells/" +str(i) + "d.jpg", answers[i-1][3])
        return answers

