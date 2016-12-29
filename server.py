from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

# -*- coding: utf-8 -*-
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from bson.objectid import ObjectId

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'TankFiller'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/TankFiller'

mongo = PyMongo(app)

@app.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def hello_world():
    return 'Hello, World!'

@app.route('/stars',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_stars():
    star = mongo.db.stars
    output = []
    for s in star.find():
      output.append({'name' : s['name'], 'distance' : s['distance']})
    return jsonify({'result' : output})

@app.route('/user/<userid>/cars',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_user_cars(userid):
    cars = mongo.db.cars
    output = []
    for c in cars.find({}):
        output.append({'model' : c['model']})
    return jsonify(output)

@app.route('/fillups',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_fillups():
    car = mongo.db.Tankfiller
    output = []
    for s in star.find():
      output.append({'name' : s['name'], 'distance' : s['distance']})
    return jsonify({'result' : output})
