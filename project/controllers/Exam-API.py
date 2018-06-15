from project import app
from project.database import db_session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_current_user
from flask_classy import FlaskView, route
from flask import jsonify, request
import datetime
# from project.model.user import User
from project.model.exam import Exam
from project.logger import Logger
# from project.controllers.utilities.user_management import Jwt_helper 



class ExamView(FlaskView):
    trailing_slash=True
    route_prefix='api'
    

    @jwt_required
    def post(self):
        if not request.is_json:
            return jsonify({"msg": "missing json request"}), 400

        name = request.json.get('name', None)
        answers_key = request.json.get('answers_key', dict())
        date = datetime.datetime.strptime(request.json.get('date', None),'%Y-%m-%d')
        description = request.json.get('description', None)
        lessons = request.json.get('lessons', dict())
        setting = request.json.get('setting', dict())
        marks = dict()
        ranks = dict()
        percentage_of_responses_to_questions = dict()
        user_id = get_current_user().id
        students = list()
        workbooks = list()
        classes = list()


        try:
            session = db_session()
            exam = Exam(name, answers_key, date, description, lessons, setting, marks, ranks, percentage_of_responses_to_questions, user_id, students, classes, workbooks)
            session.add(exam)
            session.commit()
            return jsonify(success=True), 201
        except Exception as e:
            session.rollback()
            Logger.debug("could not create new exam")
            Logger.error(e.message)
            return jsonify(success=False), 400
    
    @jwt_required
    def patch(self, id):
        exam = Exam.query.filter_by(id = id).first()
        if not request.is_json:
            return jsonify({"msg": "missing json request"}), 400
        exam.name = request.json.get('name', exam.name)
        exam.answers_key = request.json.get('answers_key', exam.answers_key)
        # exam.date = datetime.datetime.strptime(request.json.get('date', str(exam.date)),'%Y-%m-%d')
        exam.description = request.json.get('description', exam.description)
        exam.lessons = request.json.get('lessons', exam.lessons)
        exam.setting = request.json.get('setting', exam.setting)

        try:
            session = db_session()
            session.add(exam)
            session.commit()
            return jsonify(success=True), 200
        except Exception as e:
            session.rollback()
            Logger.debug("could not update exam")
            Logger.error(e.message)
            return jsonify(success=False), 400


ExamView.register(app)