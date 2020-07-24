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
from models import db, Enterprise, Brand, Integration, Platform, Clients, Order, LineItem
from create_database import init_database
from wrapper_justeat import WrapperJustEat
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

@app.cli.command("syncapi")
def syncapi():
    integration = Integration(platform_id=1)
    data= integration.getData()
    WrapperJustEat.translateAndSave(data)
    return 
    integrations = Integration.query.all()
    for integration in integrations:
        data= integration.getData()
        if (integration.platform.name == "JustEat"):
            WrapperJustEat.translateAndSave(data)

==
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
    new_brand = Brand(name=body['name'], logo=body['logo'], enterprise_id=body['enterprise_id'])
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


#METODOS PARA PLATFORM

@app.route('/platform', methods=['GET'])
def get_all_myplatform():
    all_platform = Platform.query.all()
    platforms = list(map(lambda platform: platform.serialize(), all_platform))
    return jsonify(platforms),200

@app.route('/platform/<int:id>', methods=['GET'])
def get_single_platform(id):
    single_platform = Platform.query.filter_by(id=id).first_or_404()
    return jsonify(single_platform.serialize()),200

@app.route('/platform', methods=['POST'])
def add_platform():
    body = request.get_json()
    if 'name' not in body:
        return 'please specify the platform´s name', 400
    new_platform = Platform(name=body['name'])
    db.session.add(new_platform)
    db.session.commit()
    return jsonify(new_platform.serialize()), 200

@app.route('/platform/<int:id>', methods=['DELETE'])
def delete_single_platform(id):
    single_platform =Platform.query.filter_by(id=id).first_or_404()
    db.session.delete(single_platform)
    db.session.commit()
    return jsonify(single_platform.serialize()),200

#METODOS PARA INTEGRATION

@app.route('/platform/integration', methods=['GET'])

@app.route('/enterprise/brand/integration', methods=['GET'])
@login_required

def get_all_integration():
    all_integration = Integration.query.all()
    integrations = list(map(lambda integration: integration.serialize(), all_integration))
    return jsonify(integrations),200


@app.route('/platform/integration', methods=['POST'])

@app.route('/enterprise/brand/integration', methods=['POST'])
@login_required

def add_integration():
    body = request.get_json()
    if 'API_key' not in body:
        return 'please specify the API_key', 400
    new_integration = Integration(API_key=body['API_key'], brand_id=body['brand_id'])
    db.session.add(new_integration)
    db.session.commit()
    return jsonify(new_integration.serialize()), 200


@app.route('/platform/integration/<int:id>', methods=['DELETE'])

@app.route('/enterprise/brand/integration/<int:id>', methods=['DELETE'])
@login_required

def delete_single_integration(id):
    single_integration =Integration.query.filter_by(id=id).first_or_404()
    db.session.delete(single_integration)
    db.session.commit()
    return jsonify(single_integration.serialize()),200


@app.route('/platform/integration/<int:id>', methods=['PUT'])

@app.route('/enterprise/brand/integration/<int:id>', methods=['PUT'])
@login_required

def update_integration(id):
    body = request.get_json()
    update_single_integration =Integration.query.filter_by(id=body['id']).first_or_404()
    update_single_integration.API_key = body['API_key']
    update_single_integration.brand_id = body['brand_id']
    db.session.commit()
    return jsonify(update_single_integration.serialize()),200

#METODOS PARA ORDER


@app.route('/enterprise/brand/order', methods=['GET'])
def get_all_order():
    all_order = Order.query.all()
    orders = list(map(lambda order: order.serialize(), all_order))
    return jsonify(orders),200

@app.route('/enterprise/brand/order/<int:id>', methods=['GET'])
def get_single_order(id):
    single_order = Order.query.filter_by(id=id).first_or_404()
    return jsonify(single_order.serialize()),200

@app.route('/enterprise/brand/order', methods=['POST'])
def add_order():
=======
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
    if 'date' not in body:
        return 'please specify the date', 400
    if 'total_price' not in body:
        return 'please specify the total price', 400
    if 'review' not in body:
        return 'please specify the review', 400
    new_order = Order(date=body['date'], total_price=body['total_price'], review=body['review'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify(new_order.serialize()), 200

#METODOS PARA LINEITEM


@app.route('/enterprise/brand/order/line-item', methods=['GET'])
def get_all_line_item():
    all_line_item = LineItem.query.all()
    line_item = list(map(lambda line_item: line_item.serialize(), all_line_item))
    return jsonify(line_item),200

@app.route('/enterprise/brand/order/line-item/<int:id>', methods=['GET'])
def get_single_line_item(id):
    single_line_item = LineItem.query.filter_by(id=id).first_or_404()
    return jsonify(single_line_item.serialize()),200

@app.route('/enterprise/brand/order/line-item', methods=['POST'])
def add_line_item():
=======
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
    if 'product_name' not in body:
        return 'please specify the product name', 400
    if 'quantity' not in body:
        return 'please specify the quantity', 400
    if 'price' not in body:
        return 'please specify the price', 400
    new_line_item = Order(product_name=body['product_name'], quantity=body['quantity'], price=body['price'])
    db.session.add(new_line_item)
    db.session.commit()
    return jsonify(new_line_item.serialize()), 200



if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
