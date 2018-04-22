import numpy as np
import cv2
class Scoring:

    @staticmethod
    def extractData(answers, sensitivity = 180):
        scored = {}
        for row in xrange(340):
            answer = []
            for column in range(1, 5):
                question = answers[row][column - 1]
                _, thresh = cv2.threshold(question, 127, 255, cv2.THRESH_BINARY_INV)
                mask = np.ones(thresh.shape, dtype="uint8")
                mask = cv2.bitwise_and(thresh, thresh, mask= mask)
                total = cv2.countNonZero(thresh)
                if total >= sensitivity:
                    answer.append((column))
            scored[row + 1] = answer
        return scored
