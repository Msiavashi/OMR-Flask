from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean
from sqlalchemy.types import BigInteger, TIMESTAMP
from sqlalchemy.orm import relationship, backref
import datetime
from project.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(50), nullable=False)
    national_id = Column(String(25), nullable=False)
    username = Column(String(25), nullable=False)
    password = Column(String(40), nullable=False)
    account_activated = Column(Boolean, nullable=False)
    registered_date = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    classes = relationship("Class", lazy='subquery')
    students = relationship("Student", lazy='subquery')
    exams = relationship("Exam", lazy='subquery')
    # roles = relationship('Role', secondary="roles_users_junction_table", back_populates="users")

    def __init__(self, first_name, last_name, email, national_id, username, password, account_activated, classes, students, exams):
        self.first_name = first_name
        self.exams = exams
        self.students = students
        self.classes = classes
        # self.registered_date = registered_date
        self.account_activated = account_activated
        self.password = password
        self.username = username
        self.national_id = national_id
        self.email = email
        self.last_name = last_name
        # self.roles = roles
