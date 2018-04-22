from project.applications.exam.logger import *
import operator
from answer_sheet.Sheet_Generator import *
from MultipleChoiceScanner import Scanner
from project.applications.exam.controller.custom_exceptions.answerAreaROIException import AnswerAreaROIException
from project.applications.exam.controller.custom_exceptions.dataExtractionException import DataExtractionException
from project.applications.exam.controller.custom_exceptions.barcodeException import BarcodeReadingException
from project.model.workbook import Workbook
from project.database import db_session
import datetime
from project.model.student import Student
from exam_corrector import Corrector
import os
from project.controllers.utilities.storage import Private_Storage


class Holder:
    
    def __init__(self, exam, total_number_of_question):
        self.total_number_of_question = total_number_of_question
        self.exam = exam
        self.__corrector = Corrector(exam, total_number_of_question)

    def generate_all_sheets(self, save_addr, tmp_addr, template_addr):
        print "save_addr"
        print save_addr
        print "tmp_addr"
        print tmp_addr
        print "template_addr"
        print template_addr
        generator = Sheet_Generator(template_addr, tmp_addr, save_addr,110, 20, 6, 750, 170, 720, 120, "arial.ttf", 18, 18,(0, 0, 0))
        try:
            print self.exam
            for student in self.exam.students:
                print student
                generator.generate(student.first_name, student.last_name, student.student_id)
        except Exception as e:
            Logger.debug("could not generate sheet for students")
            Logger.error(e.message)

            
    def generate_sheet_for_student(self, student, save_addr="./sheets/", tmp_addr="tmp.png", template_addr="answer_sheet/sheet.tif"):
        #TODO: zip the folder
        generator = Sheet_Generator(template_addr, tmp_addr, save_addr,110, 20, 6, 750, 170, 720, 120, "arial.ttf", 18, 18,(0, 0, 0))
        try:
            generator.generate(student.first_name, student.last_name, student.student_id)
        except Exception as e:
            Logger.debug("could not generate sheet for students")
            Logger.error(e.message)


    def _update_presents(self, presents_id):

        session = db_session()
        try:
            workbooks = session.query(Workbook).filter(Workbook.exam_id == self.exam.id).all()

            for workbook in workbooks:
                if session.query(Student).filter(Student.id == workbook.student_id).first().student_id in presents_id:
                    workbook.presence = True
                else:
                    workbook.presence = False

                session.add(workbook)
                session.commit()
            session.close()
        except Exception as e:
            Logger.debug("could not update the presents in database")
            Logger.error(e.message)

        finally:
            session.close()




    def scan_sheets(self, src_addr, dst_addr, error_addr, scan_sensitivity):
        #TODO scan the filled sheets & log the errors and informations

        all_results = {}

        if not os.path.exists(src_addr):
            os.makedirs(dst_addr)
        if not os.path.exists(error_addr):
            os.makedirs(error_addr)

        files = [os.path.join(src_addr, f) for f in os.listdir(src_addr) if os.path.isfile(os.path.join(src_addr, f)) and not f.endswith(".db")]
        scanner = Scanner.Scanner()
        presents = []
        for file in files:
            try:
                result, barcode = scanner.scan_sheet(open(file, "r"), scan_sensitivity)
                presents.append(barcode)
                all_results[barcode] = result
            except IOError as e:
                Logger.error(e.message)
            except AnswerAreaROIException as ROI_error:
                Logger.error(ROI_error.message)
            except BarcodeReadingException as barcode_error:
                Logger.debug("could not read the barcode")
                Logger.error(barcode_error.message)
            except DataExtractionException as data_extraction_error:
                Logger.error(data_extraction_error.message)

        self._update_presents(presents)

        return all_results


    def update_workbook_with_given_answers(self, workbooks_answers_dic):
        try:
            for workbook, answers in workbooks_answers_dic.items():
                workbook.answers = answers
        except Exception as e:
            Logger.debug("could not update the exams with answers for workbooks")
            Logger.error(e.message)


    def generate_workbook_for_students(self):
        session = db_session()
        for student in self.exam.students:
            workbook = Workbook(datetime.datetime.now(), {}, {}, False, student.id, self.exam.id)
            student.workbooks.append(workbook)
            # session = session.object_session(student)
            session.add(student)
            session.commit()
        session.close()


    def scan_single_sheet(self, student):
        #TODO scan a single sheet
        pass

    def get_scan_information(self):
        #TODO return the information of latest scan (erros , logs and ...)
        pass
    
    def get_presents(self):
        #TODO return all present students
        pass

    def run_correction(self):
        session = db_session()
        #calculate true or false answers
        workbooks_evaluated_answers_dic = self.__corrector.evaluate_answers_for_all()

        session = db_session()

        #calculate and write percentages to database
        workbooks_percentages_dic = self.__corrector.calculate_percentage_for_all_students(workbooks_evaluated_answers_dic)

        #calculate balance to each lesson and for all students
        workbooks_balances_dic = self.__corrector.calculate_lessons_balance_for_all(workbooks_percentages_dic)

        #calculate ranks for each lesson for all students
        workbooks_lessons_ranks_dic = self.__corrector.calculate_lessons_ranks_for_all(workbooks_balances_dic)

        #calculate total balance for each student
        workbooks_total_balances_dic = self.__corrector.calculate_total_balance_for_all(workbooks_balances_dic)

        #calculate ranks
        sorted_by_balance_tuple = sorted(workbooks_total_balances_dic.items(), key=operator.itemgetter(1))

        #write data to database
        try:
            for index, workbook, balance in enumerate(sorted_by_balance_tuple):
                result = {}
                workbook.answers = workbooks_evaluated_answers_dic[workbook]
                result["percentages"] = workbooks_percentages_dic[workbook]
                result["rank"] = index
                result["balance"] = balance
                result["total_growth"] = None
                result["lessons_rank"] = workbooks_lessons_ranks_dic[workbook]
                result["lessons_growth"] = {}
                workbook.results = result
                session.add(workbook)
                session.commit()
        except Exception as e:
            Logger.debug("could not write results to database")
            Logger.error(e.message)
        finally:
            session.close()





