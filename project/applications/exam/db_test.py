from model.student import Student
from model.exam import Exam
from model.user import User
from model.class_model import Class
from model.workbook import Workbook
import datetime
from datetime import timedelta
from controller.exam_holder import Holder
from database.db import DB

DB.start_connection()
DB.drop_db()
DB.generate_database_schema()

session = DB.Session_factory()

user1 = User("Mohammad", "Siavashi", "mohammad.siav@hotmail.com", "4490347022", "MS95", "2223858", True, [], [], [])
session.add(user1)



student1 = Student(first_name="Ahmad", last_name="siavash", expire_date = datetime.datetime.now(), advisor="ahmad", national_id="44903232527", student_id = "9332045", user_id = session.query(User).filter(User.username == "MS95").first().id, classes=[], exams=[] , workbooks=[])
session.add(student1)

student2 = Student(first_name="Zahra", last_name="Rahmaniyan", expire_date = datetime.datetime.now(), advisor="Bahareh", national_id="09366194077", student_id = "9332010", user_id = session.query(User).filter(User.username == "MS95").first().id, classes=[], exams=[] , workbooks=[])
session.add(student2)


user1.students.append(student1)
user1.students.append(student2)


class1 = Class("ClassB", "This is Class B", session.query(Student).all(), session.query(User).filter(User.username == "MS95").first().id, [])
session.add(class1)


exam2 = Exam("first exam", {"riazi": 22}, datetime.datetime.now(), "this is only for test", {}, {}, {}, {}, {}, session.query(User).filter(User.username == "MS95").first().id, session.query(Student).all(), [], [])
session.add(exam2)

session.commit()
# session.close()
# print session.query(Exam).all()[0].students
holder = Holder(session.query(Exam).all()[0], 340)



# holder.generate_all_sheets(tmp_addr="./temp/tmp.png", template_addr='./controller/answer_sheet/sheet.tif')
# holder.generate_workbook_for_students()
holder.scan_sheets(src_addr="./ans/", dst_addr="./ans/scanned/", error_addr="./ans/error/", scan_sensitivity=80)
print session.query(Workbook).all()
holder.run_correction()
