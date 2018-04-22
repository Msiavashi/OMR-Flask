from flask_inputs.validators import JsonSchema

schema = {
    'type': 'object',
    'properties':{
        'first_name': {'type': 'string'},
        'last_name': {'type': 'string'},
        'email': {'type': 'string'},
        'national_id': {'type': 'string'},
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'first_name': {'type': 'string'},
        'account_activated': {'type': 'boolean'},
        'registered_date': {'type': 'string'},
        'classes': {'type': 'string'},
        'students': {'type': 'string'},
        'exams': {'type': 'string'},
        'roles': {'type': 'string'},
    },
}

