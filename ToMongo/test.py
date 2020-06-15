import pymongo
import datetime
from functools import wraps
from time import time

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["customers"]

t = datetime.datetime.now()
name = 'you'
mydict = { "name": name, "address": "bankkok" }

def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print('Elapsed time: {}'.format(end - start))
        return result
    return wrapper
cursor = mycol.find({})


@timing
def f():
    for document in cursor:
        print(document)
f()