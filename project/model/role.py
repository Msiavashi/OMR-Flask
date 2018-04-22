from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean
from sqlalchemy.types import BigInteger, TIMESTAMP
from sqlalchemy.orm import relationship, backref
import datetime
from project.database import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(80))
    description = Column(String(512))
    # users = relationship('User', secondary="roles_users_junction_table", back_populates="roles")

    def __init__(self, name):
        self.name = name.strip().lower()
        if name == 'holder':
            self._set_description_for_teacher()

    def _set_description_for_teacher(self):
        self.description = "Exam Holder Account"