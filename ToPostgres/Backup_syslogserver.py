from datetime import datetime
import socketserver
import time

import psycopg2

def write_to_do(sql_statement, cursor, debug = False, variables = None):
    
    try:
        if debug == True:
            print('SQL statement: {}'.format(sql_statement))
            print('Variables: {}'.format(variables))
        cursor.execute(sql_statement)

        if debug == True:
            print('The last inserted id was: {}'.format(cursor.lastrowid))
        cursor.close()

    except psycopg2.Error as error:
        print('Error: {}'.format(error))

    return None

def create_db(db_name, cursor, debug = False):
    
    sql_statement = 'CREATE DATABASE {};'.format(db_name)

    write_to_do(sql_statement, cursor, debug)

    return None

def create_table(db_name, table_name, cursor, debug = False):
    sql_statement = (
        'CREATE TABLE {} ('
        'id serial PRIMARY KEY,'
        'inserted_utc timestamp default current_timestamp,'
        'message VARCHAR (256)'
        ')'
    ).format(table_name)

    write_to_do(sql_statement, cursor, debug)

    return None

def insert_data(db_name, table_name, cursor, data, debug = False):
    sql_statement = (
        'INSERT INTO {} (message) VALUES ("{}")'
        # 'inserted_utc = %s,'
        # 'message = %s'
    ).format(table_name, data)
    variables = (datetime.now(), data)

    write_to_do(sql_statement, cursor, variables=variables)

    return None

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """
    Decodes syslog data and add timestamp.

    This class takes the recieved syslog entries and writes them to the database.
    """

    def handle(self):
        try:
            postgres_connector = psycopg2.connect(user = self.server.db_user, password = self.server.db_password, host = self.server.db_host, port = self.server.db_port)
        except psycopg2.Error as error:
            print('Error: {}').format(error)

        data = bytes.decode(self.request[0].strip(), encoding="utf-8")

        cursor = postgres_connector.cursor()
        insert_data(self.server.db_name, self.server.table_name, cursor, data)

        postgres_connector.commit()

        postgres_connector.close()

        print('At {} recieved following message: {}'.format(time.time(), data))

if __name__ == "__main__":
    
    HOST, PORT = "0.0.0.0", 12312

    db_name = 'logging'
    table_name = 'logs'
    db_user = 'postgres'
    db_password = 'changeme'
    db_host = 'localhost'
    db_port = 5432

    try:
        postgres_connector = psycopg2.connect(user = db_user, password = db_password, host = db_host, port = db_port, database = db_name)
        cursor = postgres_connector.cursor()
    except Exception as e:
        print('Error: {}'.format(e))
    

    cursor = postgres_connector.cursor()
    # create_table(db_name, table_name, cursor)

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