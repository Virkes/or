from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

conn = psycopg2.connect(database="OR",
                        user='postgres',
                        password=os.environ.get('PASSWORD'),
                        host='127.0.0.1',
                        port='5433')


app = Flask(__name__)
CORS(app)

conn.autocommit = True
cursor = conn.cursor()

@app.route('/')
def datatable():
    sql = '''
    SELECT *
    FROM wild_life
    JOIN observing
    ON wild_life.chip_number = observing.animal_chip
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return jsonify(result)

if __name__ == "__main__":
    app.run()