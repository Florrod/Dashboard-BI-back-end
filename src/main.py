"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, json, render_template, redirect, url_for, abort
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from url_helper import is_safe_url
from flask_wtf import FlaskForm
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Enterprise, Brand, Integration, Mydata, Platform
from create_database import init_database
from login_form import MyForm
from flask_bootstrap import Bootstrap
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_raw_jwt, get_jwt_identity, create_refresh_token, jwt_refresh_token_required)
#from models import Person


app = Flask(__name__)
Bootstrap(app)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_database()
login_manager = LoginManager()
login_manager.init_app(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

#Configuración JWT Flask Extended
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)

blacklist = set()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@login_manager.user_loader
def load_user(user_id):
    return Enterprise.get_some_user_id(user_id=user_id)

@app.route('/login', methods=['POST'])
def login():
    # # Here we use a class of some kind to represent and validate our
    # # client-side form data. For example, WTForms is a library that will
    # # handle this for us, and we use a custom LoginForm to validate.
    # form = MyForm()
    # if form.validate_on_submit():
    #     # Login and validate the user.
    #     # user should be an instance of your `User` class

    #     user = Enterprise.get_user(email=form.email.data, password=form.password.data)
        
    #     login_user(user)

    #     next = request.args.get('next')
    #     # is_safe_url should check if the url is safe for redirects.
    #     # See http://flask.pocoo.org/snippets/62/ for an example.
    #     if not is_safe_url(next):
    #         return abort(400)

    #     return redirect(next or url_for('sitemap'))
    # return render_template('login.html', form=form)
    if not request.is_json:
        return jsonify({'msg': 'Missing JSON in request'}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email:
        return jsonify({'msg': 'Missing email parameter'}), 400
    if not password:
        return jsonify({'msg': 'Missing password parameter'}), 400

    user = Enterprise.getEnterpriseWithLoginCredentials(email, password)

    if user == None:
        return jsonify({'msg': 'La empresa o contraseña no existen'}), 400

    access_token = create_access_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': create_refresh_token(identity=user.id)
    }), 200

@app.route('/refresh' , methods=['POST'])
@jwt_refresh_token_required
def refresh():
    user_id = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=user_id)
    }
    return jsonify(ret), 200

@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'msg': 'Successfully logged out'}), 200


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#METODOS PARA ENTERPRISE

@app.route('/enterprise', methods=['GET'])
@login_required
def get_all_enterprises():
    all_enterprises = Enterprise.query.all()
    enterprises = list(map(lambda enterprise: enterprise.serialize(), all_enterprises))
    return jsonify(enterprises),200

@app.route('/enterprise/<int:id>', methods=['GET'])
@login_required
def get_single_enterprise(id):
    single_enterprise =Enterprise.query.filter_by(id=id).first_or_404()
    return jsonify(single_enterprise.serialize()),200

@app.route('/enterprise/<int:id>', methods=['DELETE'])
@login_required
def delete_single_enterprise(id):
    single_enterprise =Enterprise.query.filter_by(id=id).first_or_404()
    db.session.delete(single_enterprise)
    db.session.commit()
    return jsonify(single_enterprise.serialize()),200

@app.route('/enterprise/<int:id>', methods=['PUT'])
@login_required
def update_enterprise(id):
    body = request.get_json()
    update_single_enterprise =Enterprise.query.filter_by(id=body['id']).first_or_404()
    update_single_enterprise.CIF_number = body['CIF_number']
    update_single_enterprise.name = body['name']
    update_single_enterprise.password = body['password']
    update_single_enterprise.address = body['address']
    update_single_enterprise.phone = body['phone']
    update_single_enterprise.email = body['email']
    update_single_enterprise.is_active = body['is_active']
    db.session.commit()
    return jsonify(update_single_enterprise.serialize()),200

@app.route('/enterprise', methods=['POST'])
@login_required
def add_enterprise():
    body = request.get_json()
    if 'CIF_number' not in body:
        return 'please specify CIF_number',400
    if 'name' not in body:
        return 'please specify the name of the company', 400
    if 'password' not in body:
        return 'please specify your password', 400
    if 'address' not in body:
        return 'please specify the address of the company', 400
    if 'phone' not in body:
        return 'please specify the phone of the company', 400
    if 'email' not in body:
         return 'please specify the email of the company', 400
    if 'is_active' not in body:
        return 'please specify the status of the company', 400
    new_enterprise = Enterprise(CIF_number=body['CIF_number'], name=body['name'], password=body['password'], address=body['address'], phone=body['phone'], email=body['email'], is_active=body['is_active'])
    db.session.add(new_enterprise)
    db.session.commit()
    return jsonify(new_enterprise.serialize()), 200

#METODOS PARA BRAND

@app.route('/enterprise/brand', methods=['GET'])
@login_required
def get_all_brand():
    all_brand = Brand.query.all()
    brands = list(map(lambda brand: brand.serialize(), all_brand))
    return jsonify(brands),200

@app.route('/enterprise/brand/<int:id>', methods=['GET'])
@login_required
def get_single_brand(id):
    single_brand =Brand.query.filter_by(id=id).first_or_404()
    return jsonify(single_brand.serialize()),200

@app.route('/enterprise/brand', methods=['POST'])
@login_required
def add_brand():
    body = request.get_json()
    if 'name' not in body:
        return 'please specify the name of the company', 400
    new_brand = Brand(name=body['name'], logo=body['logo'], enterprise_to_id=body['enterprise_to_id'])
    db.session.add(new_brand)
    db.session.commit()
    # new_brand.save()
    return jsonify(new_brand.serialize()), 200

@app.route('/enterprise/brand/<int:brand_id>', methods=['PUT'])
@login_required
def update_brand(brand_id):
    body = request.get_json()
    update_single_brand =Brand.query.filter_by(id=body['id']).first_or_404()
    update_single_brand.name = body['name']
    update_single_brand.logo = body['logo']
    db.session.commit()
    return jsonify(update_single_brand.serialize()),200

@app.route('/enterprise/brand/<int:id>', methods=['DELETE'])
@login_required
def delete_single_brand(id):
    single_brand =Brand.query.filter_by(id=id).first_or_404()
    db.session.delete(single_brand)
    db.session.commit()
    return jsonify(single_brand.serialize()),200

#METODOS PARA INTEGRATION

@app.route('/enterprise/brand/integration', methods=['GET'])
@login_required
def get_all_integration():
    all_integration = Integration.query.all()
    integrations = list(map(lambda integration: integration.serialize(), all_integration))
    return jsonify(integrations),200

@app.route('/enterprise/brand/integration', methods=['POST'])
@login_required
def add_integration():
    body = request.get_json()
    if 'API_key' not in body:
        return 'please specify the API_key', 400
    new_integration = Integration(API_key=body['API_key'], brand_to_id=body['brand_to_id'])
    db.session.add(new_integration)
    db.session.commit()
    return jsonify(new_integration.serialize()), 200

@app.route('/enterprise/brand/integration/<int:id>', methods=['DELETE'])
@login_required
def delete_single_integration(id):
    single_integration =Integration.query.filter_by(id=id).first_or_404()
    db.session.delete(single_integration)
    db.session.commit()
    return jsonify(single_integration.serialize()),200

@app.route('/enterprise/brand/integration/<int:id>', methods=['PUT'])
@login_required
def update_integration(id):
    body = request.get_json()
    update_single_integration =Integration.query.filter_by(id=body['id']).first_or_404()
    update_single_integration.API_key = body['API_key']
    update_single_integration.brand_to_id = body['brand_to_id']
    db.session.commit()
    return jsonify(update_single_integration.serialize()),200

#METODOS PARA MYDATA

@app.route('/enterprise/brand/mydata', methods=['GET'])
@login_required
def get_all_mydata():
    all_mydata = Mydata.query.all()
    mydatas = list(map(lambda data: data.serialize(), all_mydata))
    return jsonify(mydatas),200

@app.route('/enterprise/brand/mydata/<int:id>', methods=['GET'])
@login_required
def get_single_mydata(id):
    single_data = Mydata.query.filter_by(id=id).first_or_404()
    return jsonify(single_data.serialize()),200

@app.route('/enterprise/brand/mydata', methods=['POST'])
@login_required
def add_mydata():
    body = request.get_json()
    if 'detail' not in body:
        return 'please specify the detail', 400
    if 'brand_to_id' not in body:
        return 'please specify the brand', 400
    if 'integration_to_id' not in body:
        return 'please specify the Integration', 400
    new_mydata = Mydata(detail=body['detail'], brand_to_id=body['brand_to_id'], integration_to_id=body['integration_to_id'])
    db.session.add(new_mydata)
    db.session.commit()
    return jsonify(new_mydata.serialize()), 200

#METODOS PARA PLATFORM

@app.route('/integration/platform', methods=['GET'])
@login_required
def get_all_myplatform():
    all_platform = Platform.query.all()
    platforms = list(map(lambda platform: platform.serialize(), all_platform))
    return jsonify(platforms),200

@app.route('/integration/platform/<int:id>', methods=['GET'])
@login_required
def get_single_platform(id):
    single_platform = Platform.query.filter_by(id=id).first_or_404()
    return jsonify(single_platform.serialize()),200

@app.route('/integration/platform', methods=['POST'])
@login_required
def add_platform():
    body = request.get_json()
    if 'name' not in body:
        return 'please specify the platform´s name', 400
    if 'relation_integration' not in body:
        return 'please specify the relation', 400
    new_platform = Platform(name=body['name'], relation_integration=body['relation_integration'])
    db.session.add(new_platform)
    db.session.commit()
    return jsonify(new_platform.serialize()), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
