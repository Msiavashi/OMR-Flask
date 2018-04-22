from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean
from sqlalchemy.types import BigInteger, TIMESTAMP, Time
from sqlalchemy.orm import relationship
from project.database import Base
from project.logger import Logger
# from student import Student
from exam import Exam
from user import User
from project.model.class_student_junction_table import class_student_junction_table 
from project.model.exam_class_junction_table import exam_class_junction_table
from project.model.exam_student_junction_table import exam_student_junction_table
from workbook import Workbook


class Class(Base):
    __tablename__ = 'classes'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(30), nullable=False)
    description = Column(String(250), nullable=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    students = relationship("Student", secondary='class_student_junction_table', back_populates="classes", lazy='subquery')
    exams = relationship('Exam', secondary='exam_class_junction_table', back_populates="classes", lazy='subquery')

    def __init__(self, name, description, students, user_id, exams):
        self.name = name
        self.description = description
        self.students = students
        self.user_id = user_id
        self.exams = exams

    
