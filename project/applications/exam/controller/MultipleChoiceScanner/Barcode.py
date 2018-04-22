# import zbar
import qrtools
import numpy as np
import cv2
class Barcode:

    def __init__(self, grayImage):
        # self.scanner = zbar.ImageScanner()
        # self.scanner.parse_config('enable')
        self.grayImage = grayImage
    '''
    def scan(self, img):
        rows, cols = img.shape
        raw = img.tostring()
        # image = zbar.Image(rows, cols, 'Y800', raw)
        found = self.scanner.scan(image)
        print found
        for symbol in image:
            print "decoded " + str(symbol.type), "symbol ", "%s" % str(symbol.data)
    '''
    @staticmethod
    def rotate_image(image, angle):
        # grab the dimensions of the image and then determine the
        # center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # perform the actual rotation and return the image
        return cv2.warpAffine(image, M, (nW, nH))


    def rotateBarcodeRegion(self, contour, rotationDegree):
        mask = np.zeros((self.grayImage.shape[0], self.grayImage.shape[1]), dtype="uint8")
        cv2.drawContours(mask, [contour], -1, 255, cv2.cv.CV_FILLED)
        image = cv2.bitwise_and(self.grayImage,self.grayImage, mask=mask)
        M = cv2.getRotationMatrix2D((image.shape[0] / 2, image.shape[1] / 2), rotationDegree, 1)
        image = cv2.warpAffine(image, M, (image.shape[0], image.shape[1]))
        return image

    def order_points(self, pts):
        # initialize a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype="int32")

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    def set_margin(self, box, marginPx):
        box[0] = box[0] - [marginPx, marginPx]
        box[1] = box[1] - [-marginPx, marginPx]
        box[2] = box[2] + [marginPx, marginPx]
        box[3] = box[3] + [-marginPx, marginPx]
        return box


    '''
    @:return contour to draw on the desired image
    '''
    def detect(self):
        gradX = cv2.Sobel(self.grayImage, ddepth=cv2.cv.CV_32F, dx=1, dy=0, ksize=-1)
        gradY = cv2.Sobel(self.grayImage, ddepth=cv2.cv.CV_32F, dx=0, dy=1, ksize=-1)
        gradient = cv2.subtract(gradX, gradY)
        gradient = cv2.convertScaleAbs(gradient)
        blurred = cv2.blur(gradient, (11, 11))
        _, thresh = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 3))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 26))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        cnts, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        c = sorted(cnts, key = cv2.contourArea, reverse=True)[0]
        rect = cv2.minAreaRect(c)
        box = np.int0(cv2.cv.BoxPoints(rect))

        box = self.order_points(box)

        box = self.set_margin(box, 30)
        barcode = self.split_and_warp_barcode(box)
        return barcode

    def split_and_warp_barcode(self, pts):
        rect = np.zeros((4, 2), dtype="float32")

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
        ratio = self.grayImage.shape[0] / self.grayImage.shape[1]
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
        warp = cv2.warpPerspective(self.grayImage, M, (maxWidth, maxHeight))
        return warp

    '''
    Decode QR code
    @:param filename
    @:return QR code content
    '''
    @staticmethod
    def QRDecode(filename):
        qr = qrtools.QR()
        qr.decode(filename)
        return qr.data

