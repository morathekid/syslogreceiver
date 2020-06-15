from datetime import datetime
from functools import wraps
from time import time
import json
import socketserver

import pymongo

def timing_insert(inserted_data):
    @wraps(inserted_data)
    def wrapper(*args, **kwargs):
        start = time()
        result = inserted_data(*args, **kwargs)
        end = time()
        print('Elapsed time: {}'.format(end - start))
        return result
    return wrapper

def timing_read(read_data):
    @wraps(read_data)
    def wrapper(*args, **kwargs):
        start = time()
        result = read_data(*args, **kwargs)
        end = time()
        print('Elapsed time: {}'.format(end - start))
        return result
    return wrapper

@timing_insert
def inserted_data(mongo_db,mongo_tb, data):
    # print(data)
    d = dict()
    d["data"] = data
    mongo_tb.insert(d)
    
    return None

@timing_read
def read_data(mongo_tb):
    for i in mongo_tb.find():
        print(i)
    # mongo_tb.find({})
    return None

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """
    Decodes syslog data and add timestamp.

    This class takes the recieved syslog entries and writes them to the database.
    """

    def handle(self):
        try:
            mongo_connectoer = pymongo.MongoClient(host = 'localhost', port=27017)
        except Exception as e:
            print('Error: {}'.format(e))

        data = bytes.decode(self.request[0].strip(), encoding="utf-8")

        # inserted_data(self.server.mongo_db,self.server.mongo_tb,data)

        read_data(self.server.mongo_tb)


if __name__ == "__main__":
    HOST,PORT = "0.0.0.0", 12312

    try:
        mongo_connectoer = pymongo.MongoClient(host='localhost',port=27017)
    except Exception as e:
        print('Error: {}'.format(e))

    mongo_db = mongo_connectoer["loggings"]
    mongo_tb = mongo_db["logs"]
    mongo_host = 'localhost'
    mongo_port = 27017

    server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)

    server.mongo_db = mongo_db
    server.mongo_tb = mongo_tb
    server.mongo_host = mongo_host
    server.mongo_port = mongo_port

    server.serve_forever()