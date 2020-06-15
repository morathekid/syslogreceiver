import socketserver
from datetime import datetime
import time

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_table(table_name, cursor, debug = False):
    sql_statement = "CREATE TABLE IF NOT EXISTS {} (id serial PRIMARY KEY,inserted_utc timestamp default current_timestamp, message VARCHAR (256));".format(table_name)
    cursor.execute(sql_statement)
    cursor.close()
    return None

def insert_data(table_name, cursor, data, debug = False):
    sql_statement = "INSERT INTO {} (message) VALUES ('{}');".format(table_name,data)
    cursor.execute(sql_statement)
    # postgres_connector.commit()
    cursor.close()

    return None

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """
    Decodes syslog data and add timestamp.

    This class takes the recieved syslog entries and writes them to the database.
    """

    def handle(self):

        try:
            postgres_connector = psycopg2.connect(user = self.server.db_user, password = self.server.db_password, host = self.server.db_host, port = self.server.db_port, database = self.server.db_name)
            postgres_connector.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except psycopg2.Error as error:
            print('Error: {}'.format(error))

        data = bytes.decode(self.request[0].strip(), encoding="utf-8")
        
        cursor = postgres_connector.cursor()
        insert_data(self.server.table_name,cursor,data)
        postgres_connector.close()
        print('At {} recieved follwing message: {}'.format(time.time(), data))


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 12312

    db_name = 'logging'
    table_name = 'logs'
    db_user = 'postgres'
    db_password = 'changeme'
    # db_host = '172.20.0.2'
    db_host= 'localhost'
    db_port = 5432

    try:
        postgres_connector = psycopg2.connect(user=db_user, password=db_password, host = db_host, port= db_port, database = db_name)
        postgres_connector.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    except psycopg2.Error as error:
        print('Error: {}'.format(error))

    cursor = postgres_connector.cursor()
    create_table(table_name, cursor)

    postgres_connector.commit()

    postgres_connector.close()

    server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)

    server.db_name = db_name
    server.table_name = table_name
    server.db_user = db_user
    server.db_password = db_password
    server.db_host = db_host
    server.db_port = db_port

    server.serve_forever()
    