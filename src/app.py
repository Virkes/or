from flask import Flask, jsonify, request, make_response, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import os
from exceptions import NotFoundException
import os.path

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


@app.route('/wild-life')
def get_all_wild_life():
    sql = '''
    SELECT row_to_json(r, true)
    FROM ( SELECT
    w.chip_number, w.kingdom,
    w.division, w.class,
    w.order, w.family,
    w.genus, w.species,
    w.biologist, w.country,
    w.sex,
    json_agg(json_build_object(
    'year', observing.year,
    'condition', observing.condition,
    'needs_attention', observing.needs_attention)) AS observed
    FROM wild_life w
    LEFT JOIN observing
    ON w.chip_number = observing.animal_chip
    GROUP BY w.chip_number)
    as r
    '''
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        wild_life = []
        for row in result:
            wild_life.extend(row)
        result_dict = {
            "status": "OK",
            "message": "Fetched all wild life",
            "response": wild_life
        }
        return make_response(jsonify(result_dict), 200)
    except Exception:
        result_dict = {
            "status": "Error",
            "message": "Server error",
            "response": "",
        }
        return make_response(jsonify(result_dict), 500)


@app.route('/wild-life/<int:chip_number>', methods=['GET'])
def get_wild_life(chip_number):
    sql = f'''
    SELECT row_to_json(r, true)
    FROM ( SELECT
    w.chip_number, w.kingdom,
    w.division, w.class,
    w.order, w.family,
    w.genus, w.species,
    w.biologist, w.country,
    w.sex,
    json_agg(json_build_object(
    'year', observing.year,
    'condition', observing.condition,
    'needs_attention', observing.needs_attention)) AS observed
    FROM wild_life w
    LEFT JOIN observing
    ON w.chip_number = observing.animal_chip
    WHERE w.chip_number = {chip_number}
    GROUP BY w.chip_number)
    as r
    '''
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            result_dict = {
                    "status": "OK",
                    "message": "Fetched one wild life",
                    "response": result[0]
                }
            return make_response(jsonify(result_dict), 200)
        raise NotFoundException
    except NotFoundException:
        result_dict = {
        "status": "Not Found",
        "message": "Wild life with the provided chip number does not exist",
        "response": "",
        }
        return make_response(jsonify(result_dict), 404)
    except Exception:
        result_dict = {
            "status": "Error",
            "message": "Server error",
            "response": "",
        }
        return make_response(jsonify(result_dict), 500)

@app.route('/wild-life/<int:chip_number>', methods=['PUT'])
def update_wild_life(chip_number):
    try:
        request_data = request.get_json()

        if "id" in request_data:
            if "needs_attention" in request_data:
                sql = f'''
                UPDATE observing
                SET needs_attention = '{request_data["needs_attention"]}'
                WHERE id = {request_data["id"]}
                '''
                cursor.execute(sql)

            if "condition" in request_data:
                sql = f'''
                UPDATE observing
                SET condition = '{request_data["condition"]}'
                WHERE id = {request_data["id"]}
                '''

        if "sex" in request_data:
            sql = f'''
            UPDATE wild_life
            SET sex = '{request_data["sex"]}'
            WHERE chip_number = {request_data["chip_number"]}
            '''
            cursor.execute(sql)

        if "biologist" in request_data:
            sql = f'''
            UPDATE wild_life
            SET biologist = '{request_data["biologist"]}'
            WHERE chip_number = {request_data["chip_number"]}
            '''
            cursor.execute(sql)

        if "country" in request_data:
            sql = f'''
            UPDATE wild_life
            SET country = '{request_data["country"]}'
            WHERE chip_number = {request_data["chip_number"]}
            '''
            cursor.execute(sql)

        conn.commit()
        result_dict = {
            "status": "Updated",
            "message": "Wild life updated",
            "response": "",
        }
        return make_response(jsonify(result_dict), 200)
    
    except Exception:
        result_dict = {
        "status": "Not Found",
        "message": "Wild life with the provided chip number does not exist",
        "response": "",
        }
        return make_response(jsonify(result_dict), 404)


@app.route('/wild-life/<int:chip_number>', methods=['DELETE'])
def delete_wild_life(chip_number):
    try:
        sql = f'''
        DELETE FROM wild_life
        WHERE chip_number = {chip_number}
        '''
        cursor.execute(sql)
        conn.commit()
        result_dict = {
            "status": "Deleted",
            "message": "Wild life deleted",
            "response": "",
        }
        return make_response(jsonify(result_dict), 200)
    except Exception:
        result_dict = {
        "status": "Not Found",
        "message": "Wild life with the provided chip number does not exist",
        "response": "",
        }
        return make_response(jsonify(result_dict), 404)


@app.route('/animals')
def get_all_animals():
    sql = '''
    SELECT row_to_json(r, true)
    FROM ( SELECT
    w.chip_number, w.kingdom,
    w.division, w.class,
    w.order, w.family,
    w.genus, w.species,
    w.biologist, w.country,
    w.sex
    FROM wild_life w)
    as r
    '''
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        animals = []
        for row in result:
            animals.append(row)
        result_dict = {
            "status": "OK",
            "message": "Fetched all animals",
            "response": animals
        }
        return make_response(jsonify(result_dict), 200)
    except Exception:
        result_dict = {
            "status": "Error",
            "message": "Server error",
            "response": "",
        }
        return make_response(jsonify(result_dict), 500)


@app.route('/observings')
def get_all_observings():
    sql = '''
    SELECT row_to_json(r, true)
    FROM ( SELECT animal_chip,
    year, condition,
    needs_attention
    FROM observing)
    as r
    '''
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        observings = []
        for row in result:
            observings.extend(row)
        result_dict = {
            "status": "OK",
            "message": "Fetched all observings",
            "response": observings
        }
        return make_response(jsonify(result_dict), 200)
    except Exception:
        result_dict = {
            "status": "Error",
            "message": "Server error",
            "response": "",
        }
        return make_response(jsonify(result_dict), 500)


@app.route('/wild-life/needs-attention')
def get_all_wild_life_that_needs_help():
    sql = '''
    SELECT row_to_json(r, true)
    FROM ( SELECT
    w.chip_number, w.kingdom,
    w.division, w.class,
    w.order, w.family,
    w.genus, w.species,
    w.biologist, w.country,
    w.sex,
    json_agg(json_build_object(
    'year', observing.year,
    'condition', observing.condition,
    'needs_attention', observing.needs_attention)) AS observed
    FROM wild_life w
    JOIN observing
    ON w.chip_number = observing.animal_chip
    WHERE observing.needs_attention = 't'
    GROUP BY w.chip_number)
    as r
    '''
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        wild_life = []
        for row in result:
            wild_life.extend(row)
        result_dict = {
            "status": "OK",
            "message": "Fetched all wild life that needs help",
            "response": wild_life
        }
        return make_response(jsonify(result_dict), 200)
    except Exception:
        result_dict = {
            "status": "Error",
            "message": "Server error",
            "response": "",
        }
        return make_response(jsonify(result_dict), 500)


@app.route('/new-wild-life', methods=['POST'])
def create_wild_life():
    try:
        request_data = request.get_json()

        sql = f'''
        INSERT INTO wild_life(chip_number, kingdom,
        division, "class", "order", "family", genus,
        species)
        VALUES({request_data["chip_number"]},
        '{request_data["kingdom"]}', '{request_data["division"]}',
        '{request_data["class"]}', '{request_data["order"]}',
        '{request_data["family"]}', '{request_data["genus"]}',
        '{request_data["species"]}')
        '''
        cursor.execute(sql)
        if "sex" in request_data:
            sql = f'''
            UPDATE wild_life
            SET sex = '{request_data["sex"]}'
            WHERE chip_number = {request_data["chip_number"]}
            '''
            cursor.execute(sql)

        if "biologist" in request_data:
            sql = f'''
            UPDATE wild_life
            SET biologist = '{request_data["biologist"]}'
            WHERE chip_number = {request_data["chip_number"]}
            '''
            cursor.execute(sql)

        if "country" in request_data:
            sql = f'''
            UPDATE wild_life
            SET country = '{request_data["country"]}'
            WHERE chip_number = {request_data["chip_number"]}
            '''
            cursor.execute(sql)

        if "year" in request_data:
            sql = f'''
            INSERT INTO observing(year, condition, animal_chip, id)
            VALUES({request_data["year"]}, '{request_data["condition"]}',
            '{request_data["chip_number"]}', {request_data["id"]})
            '''
            cursor.execute(sql)

            if "needs_attention" in request_data:
                sql = f'''
                UPDATE observing
                SET needs_attention = '{request_data["needs_attention"]}'
                WHERE id = {request_data["id"]}
                '''
                cursor.execute(sql)
        
        conn.commit()
        result_dict = {
                "status": "Created",
                "message": "Created a new wild life",
                "response": ""
            }
        return make_response(jsonify(result_dict), 201)
    
    except Exception:
        result_dict = {
        "status": "Error",
        "message": "Bad request",
        "response": "",
        }
        return make_response(jsonify(result_dict), 400)

@app.route('/openapi')
def get_openapi():
    f = os.path.join(os.path.dirname(__file__), os.pardir, 'openapi.json')
    return send_file(f, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)