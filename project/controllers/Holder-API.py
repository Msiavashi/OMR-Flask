
import jsonpickle
import os
from project import app
from project.database import db_session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_current_user
from flask_classy import FlaskView, route
from flask import jsonify, request
import datetime
from project.model.user import User
from project.model.class_model import Class
from project.logger import Logger
from project.controllers.utilities.user_management import Jwt_helper 
# from project.controllers.utilities.class_management import Json_helper
from project.model.student import Student
from project.model.exam import Exam 
from project.applications.exam.controller.exam_holder import Holder
from project.controllers.utilities.storage import TEMP_Storage, Private_Storage, Public_Storage


class HolderView(FlaskView):
    trailing_slash=True
    route_prefix='api'
    
        
        

    @route('/exam/<int:exam_id>/generate/sheets/', methods=['GET'])
    @jwt_required
    def generate_sheets(self, exam_id):
        try:
            holder = Holder(Exam.query.filter_by(id=exam_id).first(), 340)
            holder.generate_all_sheets(tmp_addr=os.path.join(TEMP_Storage().get_png_temp_addr(), 'tmp.png'), template_addr=TEMP_Storage().get_sheet_template_addr(), save_addr=Private_Storage().get_sheets_dir_for(exam_id))
            return jsonify(success=True), 200
        except Exception as e:
            Logger.debug("could not create new exam")
            Logger.error(e.message)
            return jsonify({"success": False, "msg": e.message}), 400

    @route('/exam/<int:exam_id>/initiate/workbooks/', methods=['GET'])
    @jwt_required
    def initiate_workbooks(self, exam_id):
        exam = Exam.query.filter_by(id=exam_id).first()
        holder = Holder(exam, 340)
        try:
            holder.generate_workbook_for_students()
            return jsonify(success=True), 200
        except Exception as e:
            Logger.error(e.message)
            return jsonify({"success": False, "msg": e.message}), 400

    @route('/exam/<int:exam_id>/scan/sheets/', methods=['GET'])
    @jwt_required
    def scan_sheets(self, exam_id):
        exam = Exam.query.filter_by(id=exam_id).first()
        holder = Holder(exam, 340)
        try:
            holder.scan_sheets(src_addr=Private_Storage().get_scanned_sheets_dir_for(exam_id), dst_addr="./ans/scanned/", error_addr="./ans/error/", scan_sensitivity=80)
            return jsonify(success=True), 200
        except Exception as e:
            Logger.error(e.message)
            return jsonify({"success": False, "msg": e.message}), 400

    @route('/exam/<int:exam_id>/correction/', methods=['GET'])
    @jwt_required
    def exam_correction(self, exam_id):
        exam = Exam.query.filter_by(id=exam_id).first()
        holder = Holder(exam, 340)
        try:
            holder.run_correction()
            return jsonify(success=True), 200
        except Exception as e:
            Logger.error(e.message)
            return jsonify({"success": False, "msg": e.message}), 400





HolderView.register(app)