from os import listdir
from Barcode import *
import json
from Scoring import *
from AnswerSheet import *
from os.path import isfile, join
import os
from project.logger import *
from project.applications.exam.controller.custom_exceptions.barcodeException import BarcodeReadingException
from project.applications.exam.controller.custom_exceptions.initializationException import InitializationException
from project.applications.exam.controller.custom_exceptions.answerAreaROIException import AnswerAreaROIException
from project.applications.exam.controller.custom_exceptions.dataExtractionException import DataExtractionException

class Scanner:

    '''
    saves the result in the given folder with the given file name as json
    '''
    def save_res(self, dst_folder, file_name, data, file_format):
        with open(join(dst_folder, file_name + file_format), "w") as fp:
            json.dump(data, fp)


    def scan_sheet(self, file, sensitivity):
        try:
            image = AnswerSheet(os.path.realpath(file.name))
        except Exception as e:
            raise InitializationException(e.message)

        barcode = Barcode.QRDecode(os.path.realpath(file.name))
        if not barcode:
            raise BarcodeReadingException("could not read the QR Code properly")
        
        try:
            answer_area = image.findAnswerArea()
            res = Scoring.extractData(image.getAllCells(answer_area), sensitivity)
            return res, barcode
        except AnswerAreaROIException:
            Logger.debug("could not find answere area for student : " + str(barcode))
            raise
        except  DataExtractionException:
            Logger.debug("could not extract data from sheet for student : " + str(barcode))
            raise



    '''
    scan images in the given directory and save the result in res_folder and separate errors in error_folder
    @:return scan information
    '''
    def scan_folder(self, src_folder, res_folder, error_folder, scan_sensitivity):
        if not os.path.exists(res_folder):
            os.makedirs(res_folder)
        if not os.path.exists(error_folder):
            os.makedirs(error_folder)

        files = [f for f in listdir(src_folder) if isfile(join(src_folder, f)) and not f.endswith(".db")]
        errors = []
        for f in files:
            image = AnswerSheet(join(src_folder, f))
            res = None
            if image:
                barcode = Barcode.QRDecode(join(src_folder, f))
                # TODO: log the errors array in a log file
                if not barcode: #then there is a error reading the barcode
                    try:
                        res = Scoring.extractData(image.getAllCells(image.findAnswerArea()), scan_sensitivity)
                    except ValueError as error:
                        logging.exception( "error in reading QRcode & " + error.message)
                    finally:
                        self.save_res(error_folder, f, res, ".json")
                        errors.append(join(src_folder, f))

                else:

                    try:
                        f = open(os.path.join(src_folder,'workbook_fn.json'), "w+")
                        f.write(str(barcode) + "\n")
                    except Exception as error:
                        logging.exception(error.message)
                    finally:
                        f.close()

                    save_dir = None
                    try:
                        res = Scoring.extractData(image.getAllCells(image.findAnswerArea()), scan_sensitivity)
                        save_dir = res_folder
                    except ValueError as error:
                        errors.append(join(src_folder, f))
                        save_dir = error_folder
                        logging.exception(error.message)
                    finally:
                        self.save_res(save_dir, barcode, res, ".json" )
            else:
                errors.append(join(src_folder, f))
            del image
        report = "total of scanned files : " + str(len(files)) + "\n" + "no error : " + str(len(files) - len(errors)) + "\n" + "errors : " + str(len(errors))
        return report
