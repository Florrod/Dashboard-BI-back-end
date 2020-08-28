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
from models import db, Enterprise, Brand, Integration, Platform, Clients, Order, LineItem, DatabaseManager, Product
from create_database import init_database
from wrappers import Wrapper
from login_form import MyForm
from flask_bootstrap import Bootstrap
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_raw_jwt, get_jwt_identity, create_refresh_token, jwt_refresh_token_required,get_jwt_identity)
from decorators.admin_required_decorator import admin_required

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


@app.cli.command("seed_platform")
def seed_platform():
    platforms= Platform.seed()
    for platform in platforms:
        print("Platform created:", platform)


@app.cli.command("syncapi")
def syncapi():
    integrations = Integration.all()
    for integration in integrations:
        data = integration.getData()
        wrapper = Wrapper(integration)
        orders = wrapper.wrap(data)
        for order in orders:
            order.addToDbSession()
    DatabaseManager.commitDatabaseSessionPendingChanges()
    return

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
    if not request.is_json:
        return jsonify({'msg': 'Missing JSON in request'}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email:
        return jsonify({'msg': 'Missing email parameter'}), 400
    if not password:
        return jsonify({'msg': 'Missing password parameter'}), 400

    user = Enterprise.getEnterpriseWithLoginCredentials(email, password) #instancia de empresa

    if user == None:
        return jsonify({'msg': 'La empresa o contraseña no existen'}), 400

    access_token = create_access_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': create_refresh_token(identity=user.id),
        'is_admin': user.check_is_admin()
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
@jwt_required #el front end necesita la cabecera de autorización cada vez que haya un jwt required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'msg': 'Successfully logged out'}), 200

@app.route('/protected', methods=['GET'])
@jwt_required
@admin_required
def protected(user):
    # Access the identity of the current user with get_jwt_identity
    #pedir al backend a que tipo de rol/user corresponde ese token (access_token)
    #el user que nos viene es el admin
    return jsonify(logged_in_as=user.serialize()), 200

@app.route('/protected/<int:id>', methods=['GET'])
@jwt_required
@admin_required
def protected_single(id, user):
    # Access the identity of the current user with get_jwt_identity
    #pedir al backend a que tipo de rol/user corresponde ese token (access_token)
    #el user que nos viene es el admin
    return jsonify({"user": user.serialize(), "id": id})



# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#QUERYS

#TOP PRODUCTS

@app.route('/top-products', methods=['GET'])
@jwt_required
def get_top_products():
    platforms = Platform.all()
    period = request.args.get("period")
    response = []
    for platform in platforms:
        products = Product.top_products_for_platform(platform.id, period)
        response.append(
            {
                "id": platform.id,
                "name": platform.name,
                "top_products": list(map(lambda product: product.serialize(), products))
            }
        )
    return jsonify(response), 200

#RECURRENT CLIENTS

@app.route('/recurrent-clients', methods=['GET'])
@jwt_required
def get_recurrent_clients():
    platforms = Platform.all()
    response = []
    for platform in platforms:
        recurrent_clients = Clients.recurrent_clients_for_platform(platform.id)
        response.append(
            {
                "id": platform.id,
                "name": platform.name,
                #Meter en orders_count el array de recurrent_clients parece raro, orders count pide un entero y recurrent_clientes parece un array
                "orders_count": list(map(lambda recurrent_client: recurrent_client.serialize(), recurrent_clients))
            }
        )
    return jsonify(response), 200

# TOTAL SALES

@app.route('/total-sales', methods=['GET'])
@jwt_required
def get_total_sales():
    platforms = Platform.all()
    period = request.args.get("period") #esto representa una variable que nos envia el frontend como parámetro de búsqueda en la url(las_week, last_month o total)
    response = []
    for platform in platforms:
        total_sales = Order.total_sales_for_platform(platform.id, period)
        print(total_sales)
        response.append(
            {
                "id": platform.id,
                "name": platform.name,
                "total_price": total_sales
                # "total_price": list(map(lambda total_sale: total_sale.serialize(), total_sales))
            }
        )
    return jsonify(response), 200

# SALES GRAPH
@app.route('/sales-graph', methods=['GET'])
# @jwt_required
def get_sales_graph():
    platforms = Platform.all()
    period = request.args.get("period") #esto representa una variable que nos envia el frontend como parámetro de búsqueda en la url(las_week, last_month o total)
    response = []
    for platform in platforms:
        total_sales = Order.sales_report(platform.id, period)
        print(total_sales)
        response.append(
            {
                "id": platform.id,
                "name": platform.name,
                "total_price": total_sales
                # "total_price": list(map(lambda total_sale: total_sale.serialize(), total_sales))
            }
        )
    return jsonify(response), 200

#PRUEBA SALES GRAPH
@app.route('/test', methods=['GET'])
# @jwt_required
def get_test_sales():
    total_sales = Order.sales_report(1, "month")

    return jsonify(total_sales), 200



#ENDPOINT AÑADIR EMPRESA
@app.route('/add-enterprise', methods=['POST'])
@jwt_required
def add_new_enterprise_form():
    body = request.get_json()
    new_enterprise_form= Enterprise(CIF_number=body['CIF_number'], name=body['enterprise_name'], password=body['password'], address=body['address'], phone=body['phone'], email=body['email'], is_admin=body['is_admin'])
    db.session.add(new_enterprise_form)
    db.session.commit()
    # enterprise_id = new_enterprise_form.id
    print("aaaaaa ->", new_enterprise_form.id)
    new_brand_form = Brand(name=body['brand_name'], logo=body['logo'], enterprise_id= new_enterprise_form.id)
    db.session.add(new_brand_form)
    db.session.commit()
    print(new_brand_form.id)
    print("aaa-Z", body['API_key'])
    if body['API_key']['JE'] != "":
        new_integration_form_JE= Integration(API_key=body['API_key']['JE'], brand_id=new_brand_form.id, platform_id=1)
        db.session.add(new_integration_form_JE)
    if body['API_key']['GL'] != "":
        new_integration_form_GL= Integration(API_key=body['API_key']['GL'], brand_id=new_brand_form.id, platform_id=2)
        db.session.add(new_integration_form_GL)
    db.session.commit()
    return jsonify(new_enterprise_form.serialize()), 200

#ENDPOINT AÑADIR BRAND
@app.route('/add-brand', methods=['POST'])
@jwt_required
def add_new_brand_form():
    body = request.get_json()
    current_enterprise_id = get_jwt_identity()
    current_enterprise_logged = Enterprise.get_some_user_id(current_enterprise_id)
    db.session.add(current_enterprise_logged)
    db.session.commit()
    print("aaaaaa ->", current_enterprise_logged.id)
    new_brand_form = Brand(name=body['name'], logo=body['logo'], enterprise_id= current_enterprise_logged.id)
    db.session.add(new_brand_form)
    db.session.commit()
    print(new_brand_form.id)
    print("aaa-Z", body['API_key'])
    if body['API_key']['JE'] != "":
        new_integration_form_JE= Integration(API_key=body['API_key']['JE'], brand_id=new_brand_form.id, platform_id=1)
        db.session.add(new_integration_form_JE)
    if body['API_key']['GL'] != "":
        new_integration_form_GL= Integration(API_key=body['API_key']['GL'], brand_id=new_brand_form.id, platform_id=2)
        db.session.add(new_integration_form_GL)
    db.session.commit()
    return jsonify(new_brand_form.serialize()), 200



#METODOS PARA ENTERPRISE

@app.route('/enterprise', methods=['GET'])
@jwt_required
def get_all_enterprises():
    current_enterprise_id = get_jwt_identity()
    current_enterprise_logged = Enterprise.get_some_user_id(current_enterprise_id)
    if not current_enterprise_logged.check_is_admin():
        return jsonify({'msg': 'Access denied'}), 400
    
    return Enterprise.jsonifyArray(Enterprise.query.all())

    # all_enterprises = Enterprise.query.all()
    # enterprises = list(map(lambda enterprise: enterprise.serialize(), all_enterprises))
    #     return jsonify(enterprises),200

@app.route('/enterprise/<int:id>', methods=['GET'])

@jwt_required
def get_single_enterprise(id):
    current_enterprise_id = get_jwt_identity() #la empresa que me han pedido
    current_enterprise_logged = Enterprise.get_some_user_id(current_enterprise_id)
    if current_enterprise_logged.check_is_admin() or current_enterprise_id == id:
        return jsonify(Enterprise.get_some_user_id(id).serialize()),200
    else:
        return jsonify({'msg': 'Access denied'}), 400
    # single_enterprise =Enterprise.query.filter_by(id=id).first_or_404()
    # return jsonify(check_is_admin.serialize()),200

@app.route('/enterprise/<int:id>', methods=['DELETE'])
@jwt_required
def delete_single_enterprise(id):
    # # single_enterprise =Enterprise.query.filter_by(id=id).first_or_404()
    # db.session.delete(single_enterprise)
    # db.session.commit()
    # return jsonify(single_enterprise.serialize()),200

    current_enterprise_id = get_jwt_identity() #la empresa que me han pedido
    current_enterprise_logged = Enterprise.get_some_user_id(current_enterprise_id) 
    enterprise_to_delete = Enterprise.get_some_user_id(id)
    if current_enterprise_logged.check_is_admin():
        db.session.delete(enterprise_to_delete)
        db.session.commit()
        return jsonify(enterprise_to_delete.serialize()),200 #hay que mirar si devolver la empresa vacia está bien?? No tiene sentido , devolveriamos unicamente el 200 o 204
    else:
        return jsonify({'msg': 'Access denied'}), 400

@app.route('/enterprise/<int:id>', methods=['PUT'])
def update_enterprise_top(id):
    body = request.get_json()
    print("aaaaaaaaaaa ->", body)
    update_single_enterprise =Enterprise.query.filter_by(id=id).first_or_404()
    update_single_enterprise.CIF_number = body['CIF_number']
    update_single_enterprise.name = body['name']
    key_to_lookup = 'password'
    if key_to_lookup in body and body['password'] != "":
        update_single_enterprise.password = body['password']
    update_single_enterprise.address = body['address']
    update_single_enterprise.phone = body['phone']
    update_single_enterprise.email = body['email']
    update_single_enterprise.is_active = body['is_active']
    db.session.commit()
    return jsonify(update_single_enterprise.serialize()),200

# @app.route('/enterprise/<int:id>/edit', methods=['POST'])
# def update_enterprise(id):
#     body = request.get_json()
#     update_single_enterprise =Enterprise.query.filter_by(id=id).first_or_404()
#     update_single_enterprise.CIF_number = body['CIF_number']
#     update_single_enterprise.name = body['name']
#     update_single_enterprise.password = body['password']
#     update_single_enterprise.address = body['address']
#     update_single_enterprise.phone = body['phone']
#     update_single_enterprise.email = body['email']
#     update_single_enterprise.is_active = body['is_active']
#     db.session.commit()
#     return jsonify(update_single_enterprise.serialize()),200

@app.route('/enterprise', methods=['POST'])
@jwt_required
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
    if 'is_admin' not in body:
        return 'please specify if you are an admin', 400
    new_enterprise = Enterprise(CIF_number=body['CIF_number'], name=body['name'], password=body['password'], address=body['address'], phone=body['phone'], email=body['email'], is_active=body['is_active'], is_admin=body['is_admin'])
    db.session.add(new_enterprise)
    db.session.commit()
    return jsonify(new_enterprise.serialize()), 200

#METODOS PARA BRAND

@app.route('/enterprise/brand', methods=['GET'])
@jwt_required
def get_all_brand():
    all_brand = Brand.query.all()
    brands = list(map(lambda brand: brand.serialize(), all_brand))
    return jsonify(brands),200


@app.route('/enterprise/brands', methods=['GET'])
@jwt_required
def get_enterprise_with_brands():
    enterprises_with_brands = [] #queremos devolver un array de empresas tanto en el admin como en el resto de usuarios
    current_enterprise_id = get_jwt_identity() #cogemos el ID de la empresa que esta loggeada, si es admin queremos todas las empresas-> comprobación
    current_enterprise_logged = Enterprise.get_some_user_id(current_enterprise_id)
    #comprobación : si es admin, nos devuleve todas las empresas, sino, la empresa del usuario loggeado
    if (current_enterprise_logged.check_is_admin()):
        enterprises = Enterprise.all()
    else:
        enterprises = [current_enterprise_logged]

    for enterprise in enterprises:
        enterpriseSerialized = enterprise.serialize()
        enterpriseSerialized["brand_id"] = list(map(lambda brand: brand.serialize(), enterprise.brand_id)) #serializamos las brands y las vamos metiendo en el array de la empresa que tenemos serializada
        enterprises_with_brands.append(enterpriseSerialized)
        
    return jsonify(enterprises_with_brands)
    
@app.route('/enterprise/brand/<int:id>', methods=['GET'])
@jwt_required
def get_single_brand(id):
    current_brand_id = get_jwt_identity()
    current_brand_logged = Brand.get_some_user_id(current_brand_id)
    if current_brand_id == id:
        return jsonify(Brand.get_some_user_id(id).serialize()),200
    else:
        return jsonify({'msg': 'Access denied'}), 400
    

@app.route('/enterprise/brand', methods=['POST'])
@jwt_required
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
@jwt_required
def update_brand(brand_id):
    body = request.get_json()
    update_single_brand =Brand.query.filter_by(id=body['id']).first_or_404()
    update_single_brand.name = body['name']
    update_single_brand.logo = body['logo']
    db.session.commit()

    return jsonify(update_single_brand.serialize()),200

@app.route('/edit-brand/<int:id>', methods=['PUT'])
@jwt_required
def edit_brand_form(id):
    body = request.get_json()
    update_brand =Brand.query.filter_by(id=body['id']).first_or_404()
    print("aaaaaa ->", update_brand.id)
    update_brand.name = body['name']
    print("aqui el nombre ->", update_brand.name)
    # update_brand.logo = body['logo']
    db.session.commit()
    print("aaa-Z", body['API_key'])
    for integration in update_brand.integrations:
        if body['API_key']['JE'] != "" and integration.platform_id==1:
            integration.API_key = body['API_key']['JE']
        if body['API_key']['GL'] != "" and integration.platform_id==2:
            integration.API_key = body['API_key']['GL']
    db.session.commit()
    return jsonify(update_brand.serialize()), 200

@app.route('/enterprise/brand/<int:id>', methods=['DELETE'])
@jwt_required
def delete_single_brand(id):
    single_brand =Brand.query.filter_by(id=id).first_or_404()
    db.session.delete(single_brand)
    db.session.commit()
    return jsonify(single_brand.serialize()),200

#METODOS PARA PLATFORM

@app.route('/integration/platform', methods=['GET'])
@jwt_required
def get_all_myplatform():
    all_platform = Platform.query.all()
    platforms = list(map(lambda platform: platform.serialize(), all_platform))
    return jsonify(platforms),200

@app.route('/integration/platform/<int:id>', methods=['GET'])
@jwt_required
def get_single_platform(id):
    single_platform = Platform.query.filter_by(id=id).first_or_404()
    return jsonify(single_platform.serialize()),200

@app.route('/integration/platform', methods=['POST'])
@jwt_required
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

#METODOS PARA INTEGRATION

@app.route('/enterprise/brand/integration', methods=['GET'])
@jwt_required
def get_all_integration():
    all_integration = Integration.query.all()
    integrations = list(map(lambda integration: integration.serialize(), all_integration))
    return jsonify(integrations),200

@app.route('/enterprise/brand/integration', methods=['POST'])
@jwt_required
def add_integration():
    body = request.get_json()
    if 'API_key' not in body:
        return 'please specify the API_key', 400
    new_integration = Integration(API_key=body['API_key'], brand_id=body['brand_id'])
    db.session.add(new_integration)
    db.session.commit()
    return jsonify(new_integration.serialize()), 200

@app.route('/enterprise/brand/integration/<int:id>', methods=['DELETE'])
@jwt_required
def delete_single_integration(id):
    single_integration =Integration.query.filter_by(id=id).first_or_404()
    db.session.delete(single_integration)
    db.session.commit()
    return jsonify(single_integration.serialize()),200


@app.route('/enterprise/brand/integration/<int:id>', methods=['PUT'])
@jwt_required
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