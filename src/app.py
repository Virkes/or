from flask import Flask, jsonify, request, make_response, send_file, session, redirect, url_for, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import os
import json
from exceptions import NotFoundException
import os.path
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode

load_dotenv()

conn = psycopg2.connect(database="OR",
                        user='postgres',
                        password=os.environ.get('PASSWORD'),
                        host='127.0.0.1',
                        port='5433')


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("APP_SECRET_KEY")


conn.autocommit = True
cursor = conn.cursor()


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


@app.route('/datatable')
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


@app.route('/')
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect(url_for("home"))


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + os.environ.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/profile")
def profile():
    user = session.get("user")
    if user:
        return render_template(
            "profile.html",
            session=user,
            pretty=json.dumps(session.get("user"), indent=4),
        )
    result_dict = {
            "status": "Forbidden error",
            "message": "You must be signed in to excess this page",
            "response": "",
        }
    return make_response(jsonify(result_dict), 403)


@app.route("/refresh")
def refresh():
    user = session.get("user")
    if user:
        os.system(r"python C:\Users\Lenovo\Desktop\OR\to_csv.py")
        os.system(r"python C:\Users\Lenovo\Desktop\OR\to_json.py")
        return make_response(jsonify(""))



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
        json_ld = {
            "@context": {
                "@vocab": "https://schema.org/",
                "country": "Country",
                "year": "Number"
            }
        }
        wild_life.append(json_ld)
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
    #try:
    cursor.execute(sql)
    result = cursor.fetchone()
    json_ld = {
        "@context": {
            "@vocab": "https://schema.org/",
            "country": "Country",
            "year": "Number"
        }
    }
    wild_life = [json_ld]
    wild_life.append(result[0])
    if result:
        result_dict = {
                "status": "OK",
                "message": "Fetched one wild life",
                "response": wild_life
            }
        return make_response(jsonify(result_dict), 200)
    #     raise NotFoundException
    # except NotFoundException:
    #     result_dict = {
    #     "status": "Not Found",
    #     "message": "Wild life with the provided chip number does not exist",
    #     "response": "",
    #     }
    #     return make_response(jsonify(result_dict), 404)
    # except Exception:
    #     result_dict = {
    #         "status": "Error",
    #         "message": "Server error",
    #         "response": "",
    #     }
    #     return make_response(jsonify(result_dict), 500)

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
            WHERE chip_number = {chip_number}
            '''
            cursor.execute(sql)

        if "biologist" in request_data:
            sql = f'''
            UPDATE wild_life
            SET biologist = '{request_data["biologist"]}'
            WHERE chip_number = {chip_number}
            '''
            cursor.execute(sql)

        if "country" in request_data:
            sql = f'''
            UPDATE wild_life
            SET country = '{request_data["country"]}'
            WHERE chip_number = {chip_number}
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
    #try:
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
    # except Exception:
    #     result_dict = {
    #     "status": "Not Found",
    #     "message": "Wild life with the provided chip number does not exist",
    #     "response": "",
    #     }
    #     return make_response(jsonify(result_dict), 404)


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
        json_ld = {
            "@context": {
                "@vocab": "https://schema.org/",
                "country": "Country",
                "biologist": "Person"
            }
        }
        animals.append(json_ld)
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
        json_ld = {
            "@context": {
                "@vocab": "https://schema.org/",
                "year": "Number",
                "condition": "MedicalCondition"
            }
        }
        observings.append(json_ld)
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
        json_ld = {
            "@context": {
                "@vocab": "https://schema.org/",
                "country": "Country",
                "year": "Number"
            }
        }
        wild_life.append(json_ld)
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