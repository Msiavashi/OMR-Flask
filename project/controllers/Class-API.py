import jsonpickle
from project import app
from project.database import db_session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_current_user
from flask.ext.classy import FlaskView, route
from flask import jsonify, request
import datetime
from project.model.user import User
from project.model.class_model import Class
from project.logger import Logger
from project.controllers.utilities.user_management import Jwt_helper 
# from project.controllers.utilities.class_management import Json_helper
from project.model.student import Student
from project.model.exam import Exam 




class ClassView(FlaskView):
    trailing_slash=True
    route_prefix='api'
    

    @route('/add/', methods=['POST'])
    @jwt_required
    def add(self):
        if not request.is_json:
            return jsonify({"msg": "missing json request"}), 400
        name = request.json.get("name", None)
        desciption = request.json.get("description", None)
        students = []
        user_id = get_current_user().id
        exams = []

        try:
            session = db_session()
            new_class = Class(name, desciption, students, user_id, exams)
            session.add(new_class)
            session.commit()
            return jsonify(success=True), 201
        except Exception as e:
            session.rollback()
            Logger.debug("could not create new class")
            Logger.error(e.message)
            return jsonify(success=False), 400
    
    # @route('/get/limit/<int:limit>/', methods=["GET"])
    # # @jwt_required
    # def get_exams(self, limit):
    #     try:
    #         result = User.query.filter_by(username="ms95").first().classes
    #         result = Json_helper.to_send(result)
    #         return jsonpickle.encode(result[0])
    #     except IndexError:
    #         return jsonify({'msg': 'list index out of range'}), 204




    @route('/<int:class_id>/add/students/', methods=['PUT'])
    @jwt_required
    def add_students(self, class_id):
        try:
            if not request.is_json:
                return jsonify({"msg": "missing json request"}), 400
            students = request.json.get('students', None)
            the_class = Class.query.filter_by(id=class_id).first()
            session = db_session()
            for student_id in students:
                student = Student.query.filter_by(id=student_id).first()
                student.classes.append(the_class)
                the_class.students.append(student)
                session.add(the_class)
                session.add(student)
                session.commit()
            return jsonify(success=True), 200
        except Exception as e:
            session.rollback()
            Logger.debug("could not assign students to class")
            Logger.error(e.message)
            return jsonify(success=False), 400

    
    @route('/<int:class_id>/add/exams/', methods=['PUT'])
    @jwt_required
    def add_exams(self, class_id):
        try:
            if not request.is_json:
                return jsonify({"msg": "missing json request"}), 400
            exams = request.json.get('exams', None)
            the_class = Class.query.filter_by(id=class_id).first()
            session = db_session()
            for exam_id in exams:
                exam = Exam.query.filter_by(id=exam_id).first()
                exam.students += the_class.students
                the_class.exams.append(exam)
                exam.classes.append(the_class)
                session.add(the_class)
                session.add(exam)
                session.commit()
            return jsonify(success=True), 200
        except Exception as e:
            session.rollback()
            Logger.debug("could not assign exams to class")
            Logger.error(e.message)
            return jsonify(success=False), 400


ClassView.register(app)