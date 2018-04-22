from project import app
from project.database import db_session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask.ext.classy import FlaskView, route
from flask import jsonify, request
import datetime
from project.model.user import User
# from project.model.role import Role
from project.logger import Logger


# Configs
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Routes

class Authentication(FlaskView):
    trailing_slash = False 
    route_prefix = '/api/'
    
    @route('/register/', methods=['POST'])
    def registration(self):
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        username = request.json.get('username', None)       #TODO: hash the password 
        password = request.json.get('password')
        first_name = request.json.get('first_name')
        last_name = request.json.get('last_name')
        email = request.json.get('email')
        national_id = request.json.get('national_id')
        classes = []
        students = []
        exams = []
        account_activated = True
        # roles = [Role('holder')]

        session = db_session()
        try:
            user = User(first_name, last_name, email, national_id, username, password, account_activated, classes, students, exams)
            session.add(user)
            session.commit()
            #TODO: redirect and provide JWT token and return it
            return jsonify(success=True), 201
        except Exception as e:
            session.rollback()
            Logger.debug("registration: Could not add new user to database")
            Logger.error(e.message)
            return jsonify(success=False), 400 

    @route('/login/', methods=['POST'])
    def login(self):
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        try:
            user = User.query.filter_by(username=username, password=password).first()
            if not user:
                return jsonify({"msg": "wrong username or password"}), 401

            #generating access token
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200

        except Exception as e:
            Logger.debug("login: user could not login, entered username: " + username)
            Logger.error(e.message)
            print e.message
            return jsonify({"msg": "server error"}), 500
            

Authentication.register(app)



