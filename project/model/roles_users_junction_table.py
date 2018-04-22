from sqlalchemy import Integer, Column, Text, ForeignKey, String, Boolean, Table
from sqlalchemy.types import BigInteger, TIMESTAMP, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from project.database import Base
roles_users_junction_table = Table('roles_users_junction_table',Base.metadata, 
    Column('user_id', ForeignKey('users.id')),
    Column('role_id', ForeignKey('roles.id')))
