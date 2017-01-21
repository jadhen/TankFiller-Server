from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
import datetime
from tf_util import datetime_2_js_date
client = MongoClient()
client.drop_database('TankFiller')
db = client.TankFiller

try:
    db.create_collection("users")
    db.create_collection("carModels")
    db.create_collection("cars")
except CollectionInvalid:
    print("Collections already exists")

users = db.users
id = users.insert({"name": "Jadzia", "surname": 'Henzel', 'login': "jadh",
                   'password': '12345'})

models = db.carModels
models.insert({"manufacturer_name": "Renault", "models": [{"name": 'Clio',
               "version": [{"name": '1'}, {"name": '2'}, {"name": '3'},
                           {"name": '4'}]}]})


repairs_type = db.repairs_dict
repairs_type.insert_many([{"name": "Clutch", "frequency": 5},
                          {"name": "Timing Belt", "frequency": 5},
                          {"name": "Winter Tyres", "frequency": 7},
                          {"name": "Wipes", "frequency": 3},
                          {"name": "Summer Tyres", "frequency": 7},
                          {"name": "Oil", "frequency": 1},
                          {"name": "Car battery", "frequency": 8}])


cars = db.cars
cars.insert({"userid": id, "manufacturer": "Renault", "model": "Clio 1",
             "prod_year": 2001,  "mileage": 100789,
             "fillups": [
                    {"date": datetime_2_js_date(2016, 06, 01), 'fullTank':
                     True, "liters": '25.6', "per_liter": "4.67",
                     "driven_km": 127},
                    {"date": datetime_2_js_date(2016, 06, 28), 'fullTank':
                     True, "liters": '18.6', "per_liter": "4.78",
                     "driven_km": 134},
                    {"date": datetime_2_js_date(2016, 07, 10), 'fullTank':
                     True, "liters": '21.6', "per_liter": "4.44",
                     "driven_km": 155},
                    {"date": datetime_2_js_date(2016, 07, 31), 'fullTank':
                     True, "liters": '22.1', "per_liter": "4.90",
                     "driven_km": 189},
                    {"date": datetime_2_js_date(2016, 8, 19), 'fullTank':
                     False, "liters": '10.2', "per_liter": "4.54",
                     "driven_km": 133},
                    {"date": datetime_2_js_date(2016, 9, 10), 'fullTank':
                     True, "liters": '23.2', "per_liter": "4.70",
                     "driven_km": 190},
                    {"date": datetime_2_js_date(2016, 10, 01), 'fullTank':
                     True, "liters": '19.6', "per_liter": "4.44",
                     "driven_km": 202},
                    {"date": datetime_2_js_date(2016, 10, 22), 'fullTank':
                     False, "liters": '16.4', "per_liter": "4.23",
                     "driven_km": 177},
                    {"date": datetime_2_js_date(2016, 11, 7), 'fullTank':
                     True, "liters": '20.2', "per_liter": "4.12",
                     "driven_km": 186}
                     ],
            "repairs": [{"type": {"name": "Clutch", "frequency": 5},
                         "date": datetime.datetime(2014, 10, 11),
                         "price": 2700}]})


for c in cars.find({}):
    print(c)
