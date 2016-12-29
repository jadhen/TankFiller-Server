from  pymongo import MongoClient, errors
from pymongo.errors import CollectionInvalid
import datetime
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
id = users.insert({"name" : "Jadzia", "surname" : 'Henzel', 'login': "jadh", 'password' : '12345'})

models = db.carModels
models.insert({"manufacturer_name": "Renault", "models": [{"name": 'Clio', "version": [{"name": '1'}, {"name": '2'}, {"name": '3'}, {"name": '4'}] }]})

cars = db.cars
cars.insert({"userid": id, "manufacturer": "Renault","model" : "Clio 1", "prod_year": 2001,  "mileage" : 100789, "fillups" :
    [{"date" : datetime.datetime(2016, 06, 01), 'fullTank' : True, "liters":'25.6', "per_liter" : "4.67" },
    {"date" : datetime.datetime(2016, 06, 28), 'fullTank' : True, "liters":'18.6', "per_liter" : "4.78" },
    {"date" : datetime.datetime(2016, 07, 10), 'fullTank' : True, "liters":'21.6', "per_liter" : "4.44" },
    {"date" : datetime.datetime(2016, 07, 31), 'fullTank' : True, "liters":'22.1', "per_liter" : "4.90" },
    {"date" : datetime.datetime(2016, 10, 19), 'fullTank' : False, "liters":'10.2', "per_liter" : "4.54" },
    {"date" : datetime.datetime(2016, 10, 20), 'fullTank' : True, "liters":'23.2', "per_liter" : "4.70" },
    {"date" : datetime.datetime(2016, 10, 25), 'fullTank' : True, "liters":'19.6', "per_liter" : "4.44" },
    {"date" : datetime.datetime(2016, 11, 01), 'fullTank' : False, "liters":'16.4', "per_liter" : "4.23" },
    {"date" : datetime.datetime(2016, 11, 20), 'fullTank' : True, "liters":'20.2', "per_liter" : "4.12" },]})
print(models.find({}))

for c in cars.find({}):
    print(c)
