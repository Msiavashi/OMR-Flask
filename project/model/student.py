from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean
import datetime
from sqlalchemy.types import BigInteger, TIMESTAMP, Time
from sqlalchemy.orm import relationship
from project.database import Base
from project.logger import Logger
from project.model.class_model import Class
from project.model.exam import Exam
from project.model.class_student_junction_table import class_student_junction_table 
from project.model.exam_class_junction_table import exam_class_junction_table
from project.model.exam_student_junction_table import exam_student_junction_table
from workbook import Workbook

class Student(Base):
    __tablename__ = 'students'
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    registered_date = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    # last_modify = Column(TIMESTAMP, nullable=False)
    expire_date = Column(TIMESTAMP, nullable=True, default=None)
    national_id = Column(String(25), nullable=False)
    advisor = Column(String(60), nullable=True)
    student_id = Column(String(25), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    classes = relationship("Class", secondary="class_student_junction_table", back_populates="students")
    exams = relationship('Exam', secondary="exam_student_junction_table", back_populates="students")
    workbooks = relationship("Workbook")
    
    def __init__(self, first_name, last_name, expire_date, national_id, advisor, student_id, user_id, classes, exams, workbooks):
        self.workbooks = workbooks
        self.exams = exams
        self.classes = classes
        self.user_id = user_id
        self.student_id = student_id
        self.advisor = advisor
        self.national_id = national_id
        self.expire_date = expire_date
        # self.registered_date = registered_date
        self.last_name = last_name
        self.first_name = first_name


