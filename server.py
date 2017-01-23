""" Elo
"""
# -*- coding: utf-8 -*-
from flask import Flask
from flask import jsonify
from flask_pymongo import PyMongo
from datetime import timedelta, datetime
from flask import make_response, request, current_app
from functools import update_wrapper
from bson.objectid import ObjectId
from tf_util import datetime_2_js_date
from dateutil.relativedelta import relativedelta


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


@app.route('/stars', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_stars():
    star = mongo.db.stars
    output = []
    for s in star.find():
        output.append({'name': s['name'], 'distance': s['distance']})
    return jsonify({'result': output})
# get car all data


@app.route('/car/<carid>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_cars_info(carid):
    cars = mongo.db.cars
    output = []
    for c in cars.find({'_id': ObjectId(carid)}):
        output.append({'model': c['model'], 'id': str(c['_id'])})
    return jsonify(output)


# get all user cars
@app.route('/user/<userid>/cars', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_user_cars(userid):
    cars = mongo.db.cars
    output = []
    for c in cars.find({'userid': ObjectId(userid)}):
        output.append({
            'model': c['model'], 'id': str(c['_id']),
            'manufacturer': c['manufacturer']})
    return jsonify({'cars': output})


@app.route('/user/', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_user():
    users = mongo.db.users
    output = []
    for u in users.find({}):
        output.append({
            'name': u['name'], 'surname': u['surname'],
            'id': str(u['_id'])})
    return jsonify({'user': output})


@app.route('/car/<carid>/fillups', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_fillups(carid):
    car = mongo.db.cars
    c = car.find_one({"_id": ObjectId(carid)})
    if 'fillups' not in c:
        return jsonify({'result': []})
    return jsonify({'result': c['fillups']})


@app.route('/car/<carid>/info', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_car_info(carid):
    car = mongo.db.cars
    output = []
    for c in car.find({"_id": ObjectId(carid)}):
        avg_per_100 = count_average(c)
        output.append({
            'model': c['model'], 'manufacturer': c['manufacturer'],
            'mileage': c['mileage'], 'prod_year': c['prod_year'],
            'avg_per_100': avg_per_100, 'avg_on_full_tank': '222'})
    return jsonify({'info': output})


def count_average(car):
    liters_sum = 0
    km_sum = 0
    for f in car['fillups']:
        liters_sum = liters_sum + float(f['liters'])
        km_sum = km_sum + float(f['driven_km'])
    return (liters_sum*100)/km_sum


@app.route('/car/<carid>/name', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_car_name(carid):
    car = mongo.db.cars
    output = []
    for c in car.find({"_id": ObjectId(carid)}):
        output.append({
            'model': c['model'], 'manufacturer': c['manufacturer']})
    return jsonify({'info': output})


@app.route('/car/new', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def add_new_car():
    man = request.form['manufacturer']
    mod = request.form['model']
    prod = request.form['prod_year']
    mil = request.form['mileage']
    userid = request.form['userid']
    car = mongo.db.cars
    result = car.insert_one({
        'manufacturer': man, 'model': mod, 'prod_year': prod, 'mileage': int(mil),
        'userid': ObjectId(userid), 'repairs': [], 'fillups': []})
    return jsonify({
        'acknowledged': result.acknowledged,
        'inserted_id': str(result.inserted_id)})


@app.route('/car/fillup/new', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def add_new_fillup():
    km = request.form['driven_km']
    pr = request.form['price']
    lit = request.form['liters']
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d")
    carid = request.form['carid']
    full = request.form['fulltank']
    car = mongo.db.cars
    car.update_one(
        {'_id': ObjectId(carid)},
        {'$inc': {'mileage': float(km)}})
    result = car.update_one(
        {'_id': ObjectId(carid)},
        {'$push': {'fillups': {'$each':
         [{'date': datetime_2_js_date(date.year, date.month, date.day),
          'liters': lit, 'driven_km': km, 'per_liter': pr, 'fullTank': full}],
          '$sort': {'date': 1}}}})
    return jsonify({
        'acknowledged': result.acknowledged,
        'modified_count': result.modified_count})


def soon(t1, t2):
    today = datetime.today()
    days_between_repairs = (t2 - t1).days
    days_elapsed = (today - t1).days
    if days_elapsed < 0.9*days_between_repairs:
        return False
    else:
        return True


def repair_status(date, frequency):
    date = date.replace(tzinfo=None)
    today = datetime.today()
    next_repair_date = (date + relativedelta(years=frequency)).replace(tzinfo=None)
    if next_repair_date < today:
        return "danger"
    elif soon(date, next_repair_date):
        return "warning"
    return "success"


def repair_info(name, freq):
    if freq == 1:
        info = "year"
    else:
        info = str(freq) + " years"
    return name + " should be replaced every " + info


@app.route('/car/<carid>/repairs', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_car_repairs(carid):
    car = mongo.db.cars
    c = car.find_one({"_id": ObjectId(carid)})
    for r in c['repairs']:
        name = r['type']['name']
        freq = int(r['type']['frequency'])
        r['status'] = repair_status(r['date'], freq)
        r['date'] = r['date'].strftime("%Y-%m-%d")
        r['info'] = repair_info(name, freq)
    if 'repairs' not in c:
        return jsonify({'result': []})
    return jsonify({'result': c['repairs']})


@app.route('/<carid>/repairs_dict', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_repairs_dict(carid):
    output = []
    repairs_dict = mongo.db.repairs_dict
    car_repairs = get_cars_done_repairs_name(carid)
    dict = repairs_dict.find({})
    for repair in dict:
        output.append({'name': repair['name'],
                       'frequency': repair['frequency'],
                       'already_done': repair_done(repair, car_repairs)})
    return jsonify(output)


def get_cars_done_repairs_name(carid):
    car = mongo.db.cars
    car_repairs = car.find_one({"_id": ObjectId(carid)})['repairs']
    output = []
    for r in car_repairs:
        output.append(r['type']['name'])
    return output


def repair_done(repair, repairs_list):
    return repair['name'] in repairs_list


@app.route('/car/repair/new', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def add_new_repair():
    pr = request.form['price']
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d")
    carid = request.form['carid']
    name = request.form['name']
    freq = request.form['frequency']
    car = mongo.db.cars
    result = car.update_one(
        {'_id': ObjectId(carid)},
        {'$push': {'repairs': {'$each':
         [{'date': date,
          'price': pr, 'type': {'name': name, 'frequency': int(freq)}}],
          '$sort': {'date': -1}}}})
    return jsonify({
        'acknowledged': result.acknowledged,
        'modified_count': result.modified_count})


@app.route('/car/repair/update', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def update_repair():
    pr = request.form['price']
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d")
    carid = request.form['carid']
    name = request.form['name']
    car = mongo.db.cars
    result = car.update_one(
        {'_id': ObjectId(carid), 'repairs.type.name': name},
        {'$set': {"repairs.$.price": pr, "repairs.$.date": date}})
    return jsonify({
        'acknowledged': result.acknowledged,
        'modified_count': result.modified_count})


#db.cars.update({"model":"Clio 1","repairs.type.name":"Clutch"}, {$set: {"repairs.$.price" : 10}})
