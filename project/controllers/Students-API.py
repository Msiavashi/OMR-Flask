from project import app
from project.database import db_session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_current_user
from flask_classy import FlaskView, route
from flask import jsonify, request
import datetime
from project.model.student import Student 
from project.logger import Logger
# from project.controllers.utilities.user_management import Jwt_helper 



class StudentView(FlaskView):
    trailing_slash=True
    route_prefix='api'
    

    @route('/add/', methods=['POST'])
    @jwt_required
    def add(self):
        if not request.is_json:
            return jsonify({"msg": "missing json request"}), 400

        first_name = request.json.get('first_name', None)
        last_name = request.json.get('last_name', None)
        expire_date = datetime.datetime.strptime(request.json.get('expire_date', None),'%Y-%m-%d')
        national_id = request.json.get('national_id', None)
        advisor = request.json.get('advisor', None)
        student_id = request.json.get('student_id', None)       #TODO: generate a unique vlaue instead of None
        user_id = get_current_user().id
        exams = []
        workbooks = [] 
        classes = []

        try:
            session = db_session()
            student = Student(first_name, last_name, expire_date, national_id, advisor, student_id, user_id, classes, exams,workbooks)
            session.add(student)
            session.commit()
            return jsonify(success=True), 201
        except Exception as e:
            session.rollback()
            Logger.debug("could not create student")
            Logger.error(e.message)
            print e.message
            return jsonify(success=False), 400
    

StudentView.register(app)