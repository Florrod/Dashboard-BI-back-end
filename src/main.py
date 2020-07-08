"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, json
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Enterprise
from create_database import init_database
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_database()
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

new_enterprise = Enterprise(CIF_number="", name="", address="",phone="",email="")


# jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/enterprise', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/enterprise', methods=['POST'])
def add_enterprise():
    new_CIF_number = request.form["CIF_number"]
    new_name = request.form["name"]
    new_address = request.form["address"]
    new_phone = request.form["phone"]
    new_email = request.form["email"]
    new_enterprise = Enterprise(new_CIF_number,new_name,new_address,new_phone,new_email)
    db.session.add(new_enterprise)
    db.session.commit()
    return json.dumps({'success':True}), 201, {'ContentType':'application/json'}

# @app.route('/enterprise', methods=['POST'])
# def handle_person():

#     # First we get the payload json
#     body = request.get_json()

#     if body is None:
#         raise APIException("You need to specify the request body as a json object", status_code=400)
#     if '' not in body:
#         raise APIException('You need to specify the username', status_code=400)
#     if 'email' not in body:
#         raise APIException('You need to specify the email', status_code=400)

#     # at this point, all data has been validated, we can proceed to inster into the bd
#     user1 = Person(username=body['username'], email=body['email'])
#     db.session.add(user1)
#     db.session.commit()
#     return "ok", 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
