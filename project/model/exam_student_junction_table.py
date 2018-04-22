from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean, Table
from sqlalchemy.types import BigInteger, TIMESTAMP, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from project.database import Base

exam_student_junction_table = Table('exam_student_junction_table', Base.metadata,
    Column('student_id', ForeignKey('students.id')),
    Column('exam_id', ForeignKey('exams.id'))
)