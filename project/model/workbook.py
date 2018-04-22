from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean
from sqlalchemy.types import BigInteger, TIMESTAMP, Time, PickleType 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from project.database import Base
import json


class Workbook(Base, object):
    __tablename__ = 'workbooks'
    id = Column(BigInteger, primary_key=True)
    release_date = Column(TIMESTAMP, nullable=False)
    answers = Column(PickleType, nullable=False)
    results = Column(PickleType, nullable=False)
    presence = Column(Boolean, nullable=False)
    student_id = Column("Student", ForeignKey("students.id"))
    exam_id = Column("Exams", ForeignKey("exams.id"))

    def __init__(self, release_date, answers, results, presence, student_id, exam_id):
        self.exam_id = exam_id
        self.student_id = student_id
        self.presence = presence
        self.results = results
        self.answers = answers
        self.release_date = release_date



    # @property
    # def answers(self):
    #     return self.answers
    #
    # @answers.setter
    # def answers(self, value):
    #     self.answers = value
    #
    # @property
    # def results(self):
    #     return self.results
    #
    # @results.setter
    # def results(self, result):
    #     self.results = result
    #

