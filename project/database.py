from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from db_config import Config

engine = create_engine('mysql://' + Config.username + ':' + Config.password + '@' + Config.host_name + ':' + Config.port + '/' + Config.db_name, pool_recycle=3600, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # from model.roles_users_junction_table import roles_users_junction_table
    from model.class_model import Class
    from model.user import User
    from model.class_student_junction_table import class_student_junction_table
    from model.exam import Exam
    from model.exam_class_junction_table import exam_class_junction_table
    from model.workbook import Workbook
    from model.exam_student_junction_table import exam_student_junction_table
    # from model.role import Role
    from model.student import Student

    Base.metadata.create_all(bind=engine)

print "initing..."
init_db()
print "done"