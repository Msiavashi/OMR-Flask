from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean
from sqlalchemy.types import BigInteger, TIMESTAMP, Time, PickleType 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from project.database import Base
import json
# from project.model.class_model import Class
# from project.model.student import Student
from project.model.class_student_junction_table import class_student_junction_table 
from project.model.exam_class_junction_table import exam_class_junction_table
from project.model.exam_student_junction_table import exam_student_junction_table
from workbook import Workbook
from project.logger import Logger

class Exam(Base):
    __tablename__ = 'exams'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    answers_key = Column(PickleType, nullable=True) # Json
    date = Column(TIMESTAMP, nullable = False)
    description = Column(String(250), nullable=True)
    lessons = Column(PickleType, nullable=False)  #json
    setting = Column(PickleType, nullable=False)
    marks = Column(PickleType, nullable=False)
    ranks = Column(PickleType, nullable=False)
    percentage_of_responses_to_questions = Column(PickleType, nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    students = relationship('Student', secondary="exam_student_junction_table", back_populates="exams", lazy='subquery')
    workbooks = relationship('Workbook', lazy='subquery')
    classes = relationship('Class', secondary='exam_class_junction_table', back_populates="exams", lazy='subquery')


    def __init__(self, name, answers_key, date, description, lessons, setting, marks, ranks, percentage_of_responses_to_questions, user_id, students, classes, workbooks):
        self.classes = classes
        self.students = students
        self.workbooks = workbooks
        self.user_id = user_id
        self.percentage_of_responses_to_questions = percentage_of_responses_to_questions
        self.ranks = ranks
        self.marks = marks
        self.setting = setting
        self.lessons = lessons
        self.description = description
        self.date = date
        self.answers_key = answers_key
        self.name = name


    def set_settings(self, setting):
        self.setting = setting

    def set_answers_key(self, key):
        self.answers_key = key
