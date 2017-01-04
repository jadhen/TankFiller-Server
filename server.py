from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
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
#get car all data
@app.route('/car/<carid>',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_cars_info(carrid):
    cars = mongo.db.cars
    output = []
    for c in cars.find({'_id' : ObjectId(carid)}):
        output.append({'model' : c['model'], 'id' : str(c['_id'])} )
    return jsonify(output)

#get all user cars
@app.route('/user/<userid>/cars',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_user_cars(userid):
    cars = mongo.db.cars
    output = []
    for c in cars.find({'userid' : ObjectId(userid)}):
        output.append({'model' : c['model'], 'id' : str(c['_id']), 'manufacturer' : c['manufacturer']} )
    return jsonify({'cars':output})

@app.route('/user/',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_user():
    users = mongo.db.users
    output = []
    for u in users.find({}):
        output.append({'name' : u['name'], 'surname': u['surname'], 'id': str(u['_id'])} )
    return jsonify({'user' : output})

@app.route('/car/<carid>/fillups',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_fillups(carid):
    car = mongo.db.cars
    output = []
    c = car.find_one({"_id" : ObjectId(carid)})
    return jsonify({'result' : c['fillups']})


@app.route('/car/<carid>/info',methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_car_info(carid):
    car = mongo.db.cars
    output = []
    for c in car.find({"_id" : ObjectId(carid)}):
      output.append({'model' : c['model'], 'manufacturer' : c['manufacturer'], 'mileage' : c['mileage'], 'prod_year' : c['prod_year'], 'avg_per_100' : 'xxx', 'avg_on_full_tank' :
     'yyy'})
    return jsonify({'info' : output})

@app.route('/car/new',methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def add_new_car():
    man = request.form['manufacturer']
    mod = request.form['model']
    prod = request.form['prod_year']
    mil = request.form['mileage']
    userid = request.form['userid']
    car = mongo.db.cars
    result = car.insert_one({'manufacturer' : man, 'model': mod, 'prod_year' : prod, 'mileage' : mil, 'userid' : ObjectId(userid)})
    return jsonify({'acknowledged' : result.acknowledged, 'inserted_id' : str(result.inserted_id)})

@app.route('/car/fillup/new',methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def add_new_fillup():
    km = request.form['driven_km']
    pr = request.form['price']
    lit = request.form['liters']
    date = request.form['date']
    carid = request.form['carid']
    full = request.form['fulltank']
    car = mongo.db.cars
    car.update_one({'_id' : ObjectId(carid) }, {'$inc': {'mileage': float(km)}})
    result = car.update_one({'_id' : ObjectId(carid) }, { '$push': {  'fillups': { '$each': [ { 'date' :datetime.strptime(date, "%Y-%m-%d"), 'liters' : lit, 'driven_km' : km, 'per_liter' : pr , 'fullTank' : full }],'$sort': { 'date': 1 }}}})
    return jsonify({'acknowledged' : result.acknowledged, 'modified_count' : result.modified_count})
