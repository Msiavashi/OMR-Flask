# # coding=utf-8
# from __future__ import unicode_literals
import arabic_reshaper
from bidi.algorithm import get_display
import png
from collections import deque
import cv2
import os
from PIL import Image, ImageDraw, ImageFont
import imutils
import numpy as np
from shapeDetector.shape_detector import *
import qrtools
import pyqrcode
import project.applications.exam.controller.jalali

class Sheet_Generator:
    def __init__(self, sheet_addr, tmp_addr, dst_addr, qr_x, qr_y, qr_scale, name_x, name_y, id_x, id_y, font, name_font_size, id_font_size, color):
        self.tmp_addr = tmp_addr
        self.sheet = sheet_addr
        self.dst_addr = dst_addr
        self.qr_scale = qr_scale
        self.name_x = name_x
        self.name_y = name_y
        self.id_x = id_x
        self.id_y = id_y
        self.font = font
        self.name_font_size = name_font_size
        self.id_font_size = id_font_size
        self.color = color
        self.qr_x = qr_x
        self.qr_y = qr_y


    def generate_qr(self, data, scale=6):
        qr = pyqrcode.create(str(data))
        return qr

    def decode_qr(self, file):
        qr = qrtools.QR()
        qr.decode(file)
        return qr.data

    def find_qr_roi_by_shape(self):
        image = cv2.imread(self.sheet)
        resized = imutils.resize(image, width=300)
        ratio = image.shape[0] / float(resized.shape[0])
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        # find contours in the thresholded image and initialize the
        # shape detector
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = Shape_detector()

        for c in cnts:
            # compute the center of the contour, then detect the name of the
            # shape using only the contour
            M = cv2.moments(c)
            cX = int((M["m10"] / M["m00"]) * ratio)
            cY = int((M["m01"] / M["m00"]) * ratio)
            shape = sd.detect(c)
            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape on the image
            c = c.astype("float")
            c *= ratio
            c = c.astype("int")
            cv2.drawContours(image, [c], -1, (0, 255, 255), 2)
            # show the output image
            cv2.imwrite("test.jpg", image)
            cv2.imshow("Image", image)
            cv2.waitKey(0)

    def find_qr_roi_by_contour(self):
        image = cv2.imread(self.sheet)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray,127,255,0)
        cnts, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[:5]
        sort = sorted(cnts, key = cv2.contourArea, reverse = True)
        cv2.drawContours(image, sort[1], -1, (255, 0, 0), 3)
        cv2.imwrite(self.tmp_addr, image)


    def overlay_image_by_offset(self,image1, image2, x, y):
        image1[y: y+image2.shape[0], x:x+image2.shape[1]] = image2
        return image1


    '''
        @:param ascsii string
        @:returns a tuple => bidi converted text, arabic reshaped text, unicode text
    '''
    def get_printable_unicode(self, ascii_string):
        text = unicode(ascii_string)
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(text)
        return bidi_text, reshaped, text


    def put_text_on_image(self, image, text, x, y, font, font_size, color):
        if isinstance(text, unicode):
            _, text, _ = self.get_printable_unicode(text)
            text = text[::-1]
        cv2.imwrite(self.tmp_addr, image)
        image = Image.open(self.tmp_addr)
        draw = ImageDraw.Draw(image)
        unicode_font = ImageFont.truetype(font, font_size)
        draw.text((x, y), text, font=unicode_font, fill=color)
        image.save(self.tmp_addr)
        return cv2.imread(self.tmp_addr)


    def __create_sheet(self, qr_data, full_name, id):
        sheet = cv2.imread(self.sheet)
        qr = self.generate_qr(qr_data)
        qr.png(self.tmp_addr, scale=self.qr_scale)
        # put qr code on the sheet
        image_with_qr = self.overlay_image_by_offset(sheet.copy(), cv2.imread(self.tmp_addr), self.qr_x, self.qr_y)
        #put name on sheet
        image_with_name = self.put_text_on_image(image_with_qr, full_name, self.name_x, self.name_y, self.font, self.name_font_size, self.color)
        #put id on sheet
        image_with_id = self.put_text_on_image(image_with_name, str(id), self.id_x, self.id_y, self.font, self.id_font_size, self.color)
        return image_with_id



    def generate(self, first_name, last_name, student_id):
        full_name = first_name + " " + last_name 
        image = self.__create_sheet(student_id, full_name, student_id)

        if not os.path.exists(self.dst_addr):
            os.mkdir(self.dst_addr)

        path = os.path.join(self.dst_addr, student_id + ".jpg")
        cv2.imwrite(path, image)

