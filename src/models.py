from flask_sqlalchemy import SQLAlchemy
import requests

from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, and_, func
from sqlalchemy.sql import text
from random import randint
from flask_login import UserMixin
from flask import jsonify
from json.decoder import JSONDecodeError
from datetime import datetime, timedelta
from functools import reduce

db = SQLAlchemy()

class DatabaseManager():
    @staticmethod
    def commitDatabaseSessionPendingChanges():
        db.session.commit()

class ModelMixin():
    def addToDbSession(self):
        db.session.add(self)

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def get_some_user_id(cls,user_id):
        return cls.query.filter_by(id=user_id).one_or_none()

class Enterprise(db.Model, ModelMixin):

    id = db.Column(db.Integer, primary_key=True)
    CIF_number = db.Column(db.String(10), unique=True, nullable=True)
    name = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=True) #preguntar como encriptar contraseña a la hora de crearla
    address = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(80),nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, unique=False, nullable=False)

    brand_id = db.relationship('Brand', cascade="all,delete", backref='enterprise', lazy=True)
 
    def __repr__(self):
        return '<Enterprise %r>' % self.name
    #__repr__ function should return a printable representation of the object, most likely one of the ways possible to create this object

    # def save(self):
    #     db.session.add(self)
    #     db.session.commit
    #     return self -> devolver true o false si utilizamos está función ya que lo que quieres devolver es si la enterprise se a creado o no


    @classmethod
    def get_some_user_id(cls,user_id):
        return cls.query.filter_by(id=user_id).one_or_none()

    @staticmethod
    def jsonifyArray(elements):
        return jsonify(list(map(lambda element: element.serialize(), elements)))

    def check_is_admin(self):
        return self.is_admin #eres el administrador? Si es admin es true. Es una funcion/metodo de instancia. Necesitamos una instancia. Si lo hacemos con la clase directamente está mal.
    
    @classmethod
    def getEnterpriseWithLoginCredentials(cls, email, password):
        return db.session.query(cls).filter(Enterprise.email == email).filter(Enterprise.password == password).one_or_none()
    
    @classmethod
    def get_user(cls, email, password):
        user_find = cls.query.filter_by(email=email, password=password).one()
        if user_find:
            return user_find
        else:
            return None
        
    def __repr__(self):
        return '<Enterprise %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "CIF_number": self.CIF_number,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "is_active": self.is_active,
            "brand_id": list(map(lambda x: x.serialize(), self.brand_id)),
            "is_admin": self.is_admin,
            # linea nueva insertada debajo !
            # do not serialize the password, its a security breach
        }

class Brand(db.Model,ModelMixin):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), unique=True, nullable=True)
    logo= db.Column(db.String(120), nullable=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id',ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    
    integrations = db.relationship('Integration', cascade="all,delete", backref='brand', lazy=True)
    orders = db.relationship('Order', cascade="all,delete", backref='brand', lazy=True)

    def __repr__(self):
        return '<Brand %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "logo": self.logo,
            "enterprise_id": self.enterprise_id,
            "integrations": list(map(lambda x: x.serialize(), self.integrations)),
            # "orders": list(map(lambda x: x.serialize(), self.orders)), # lo podríamos quitar ya que en este endpoint no nos interesan las orders. Iriamos a orders para verlas
        }
    # def save(self):
    #     db.session.add(self)
    #     db.session.commit
    #     return self

class Platform(db.Model, ModelMixin):
    id= db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(120), unique=True, nullable=True)

    integrations = db.relationship('Integration', backref='platform', lazy=True)
    orders = db.relationship('Order', backref='platform', lazy=True)

    JUST_EAT_ID= 1
    GLOVO_ID= 2

    platforms = [
        {
            "id": JUST_EAT_ID,
            "name": "Just Eat"
        },
        {
            "id": GLOVO_ID,
            "name": "Glovo"
        }
    ]

    def __repr__(self):
        return '<Platform %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "integrations": list(map(lambda x: x.serialize(), self.integrations)),
            "orders": list(map(lambda x: x.serialize(), self.orders))
        }  

    @classmethod
    def getWithId(cls, id):
        return db.session.query(cls).filter_by(id=id).one_or_none()

    @classmethod
    def seed(cls):
        platforms=[]
        for platform in cls.platforms:
            platform_to_insert= Platform.getWithId(id=platform["id"])
            if not platform_to_insert:
                platform_to_insert= Platform(id=platform["id"],name=platform["name"])
                platform_to_insert.addToDbSession()
        DatabaseManager.commitDatabaseSessionPendingChanges()
        return platforms


class Integration(db.Model,ModelMixin):
    id= db.Column(db.Integer, primary_key=True)
    API_key= db.Column(db.String(120), nullable=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)

    orders = db.relationship('Order', backref='integration', lazy=True)
    
    def __repr__(self):
        return '<Integration %r>' % self.API_key

    def serialize(self):
        return {
            "id": self.id,
            "API_key": self.API_key,
            "brand_id": self.brand_id,
            "orders": list(map(lambda x: x.serialize(), self.orders)),
            "platform_id": self.platform_id,
            "platform_name": self.platform.name
            # "deleted": self.deleted,
            # "relation_data": list(map(lambda x: x.serialize(), self.relation_data))
            # if not self.user.deleted else None
        }    

    def getData(self, from_date=""):
        if self.platform_id == 1:
            url = "https://private-ac88aa-justeapi.apiary-mock.com/orders"
        elif self.platform_id == 2:
            url = "http://private-anon-3a76a4fc70-glovapi.apiary-proxy.com/orders"

        response = requests.get(url)
        print("Response: ",response)
        if response.status_code == 200:
            # print(response.text)
            try:
                return response.json()
            except JSONDecodeError as identifier:
                print("Excepcion")
                return None
        
        return None
    
class Clients(db.Model, ModelMixin):
    id= db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(120), unique=True, nullable=True)
    orders_count = db.Column(db.Integer)
    customer_id_platform = db.Column(db.String(12), unique=True, nullable=True)
    phone= db.Column(db.String(12), unique=True, nullable=True)

    orders = db.relationship("Order", back_populates="client")

    #preguntar lo del campo calculado de quantity orders

    def __repr__(self):
        return '<Clients %r>' % self.id

    def serialize(self):
        return {
            # "email": self.email,
            "phone": self.phone,
            "customer_id_platform": self.customer_id_platform,
            "orders_count": self.orders_count
        } 

    def save(self):
        db.session.add(self) 

    # @classmethod
    # def getWithEmail(cls, email):
    #     return db.session.query(cls).filter_by(email=email).one_or_none()
    # ¿classmethod?

    @classmethod
    def getWithPhone(cls, phone):
        return db.session.query(cls).filter_by(phone=phone).one_or_none()

    @classmethod
    def getWithCustomerId(cls, customer_id):
        return db.session.query(cls).filter_by(id=customer_id).one_or_none()

    @classmethod
    def getWithCustomerPlatformId(cls, customer_platform_id):
        return db.session.query(cls).filter_by(customer_id_platform=customer_platform_id).one_or_none()

    # @staticmethod
    # def recurrent_clients_for_platform(platform_id):
    #     recurrent_clients=[]
    #     quantity_clients= 1
    #     rows= db.session.execute(
    #         f"select clients.orders_count, clients.phone, clients.customer_id_platform from clients,`order`, platform where `order`.platform_id = platform.id and `order`.platform_id = {platform_id} and `order`.client_id = clients.id order by clients.orders_count desc limit {quantity_clients};"
    #     )
        
    #     for row in rows:
    #         phone= row["phone"]
    #         customer_id_platform= row["customer_id_platform"]
    #         orders_count = row["orders_count"]
    #         #Estamos creando un cliente pocho, deberiamos como minimo hacer que sea obligatorio al crear un cliente que tenga un identificador único como puede ser un email o un telefono.
    #         recurrent_client = Clients(orders_count=orders_count, phone=phone, customer_id_platform=customer_id_platform)
    #         recurrent_clients.append(recurrent_client)
            
    #     return recurrent_clients

    @staticmethod
    def recurrent_clients_for_platform(platform_id, brand_id, period):
        days_ago = None
        if period == "last_week":
            days_ago = datetime.today() - timedelta(days = 7)
        elif period == "last_month":
            days_ago = datetime.today() - timedelta(days = 30)
        else: 
            days_ago = datetime.today() - timedelta(days = 2000)

        recurrent_clients = db.session.query(
            Clients.phone,
            Clients.customer_id_platform,
            db.func.count(Order.id).label("orders_qty"),
        ).join(Clients, Order.client_id == Clients.id
        ).group_by(
            Order.client_id
        ).filter(Order.platform_id == platform_id, Order.brand_id == brand_id
        ).filter(Order.date >= days_ago
        ).order_by(text("orders_qty desc")
        ).limit(1
        ).all()
    
        print("hola soy recurrent clients", recurrent_clients)

        return recurrent_clients

class Order(db.Model, ModelMixin):
    id= db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    total_price = db.Column(db.Float)
    state = db.Column(db.String(250))
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    integration_id= db.Column(db.Integer, db.ForeignKey('integration.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    client = db.relationship("Clients", back_populates="orders")
    
    lineItems = db.relationship('LineItem', cascade="all,delete", backref='order', lazy=True)

    # def __init__(self, state='delivered' or 'canceled'): 
    #     self.state = state + '!'
    def get_name_counts(self):
        counts = {}
        for item in self.lineItems:
            if item.product_name in counts:
                counts[item.product_name] += 1
            else:
                counts[item.product_name] = 1
        return counts

    def __repr__(self):
        return '<Order %r>' % self.total_price

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_price": self.total_price,
            "lineItems": list(map(lambda x: x.serialize(), self.lineItems)),
            "brand_id": self.brand_id
        }

    def save(self):
        db.session.add(self)

    @staticmethod
    def total_sales_for_platform(platform_id, brand_id, period):
        # print ("Holaaaaa platform", platform_id)
        total_sales= 0
        days_ago = None
        if period == "last_week":
            days_ago = datetime.today() - timedelta(days = 7)
        elif period == "last_month":
            days_ago = datetime.today() - timedelta(days = 30)
        else: 
            days_ago = datetime.today() - timedelta(days = 2000)
        orders = Order.query.filter_by(platform_id = platform_id, brand_id=brand_id).all()
        # print("Laaaaa order ->", orders)
        filter_orders = list(filter(lambda order: order.date >= days_ago, orders)) #Para cada elemento de un arreglo le pregunta si esto existe y si es así lo agrega cada order
        for order in filter_orders:
            total_sales += order.total_price
        return total_sales

    # @staticmethod
    # def sales_graph(platform_id, period):
    #     print ("Holaaaaa platform", platform_id)
    #     total_sales= 0
    #     days_ago = None
    #     if period == "last_week":
    #         days_ago = datetime.today().strftime("%A") - timedelta(days = 7)
    #     elif period == "last_month":
    #         days_ago = datetime.today().strftime("%A") - timedelta(days = 30)
    #     else: 
    #         days_ago = datetime.today().strftime("%B") - timedelta(days = 2000)
    #     orders = Order.query.filter_by(platform_id = platform_id).filter_by(date = days_ago)\
    #         .all()
    #     print("Ohhhh orders con fecha ->", orders)
    #     for order in orders:
    #         total_sales += order.total_price
    #     return total_sales

    @staticmethod
    def sales_report(platform_id, period):

        days_ago = datetime.today() - timedelta(days = 2000)
        orders = db.session.query(
            Order.platform_id, 
            db.func.day(Order.date),
            db.func.month(Order.date),
            db.func.year(Order.date),
            db.func.sum(Order.total_price),
        ).group_by(Order.platform_id,db.func.year(Order.date),db.func.month(Order.date),db.func.day(Order.date)).all()
        print("hola, soy una prueba de venta mes a mes", orders)
        return orders


    @staticmethod
    def sales_report_by_year(platform_id, period):
        days_ago = datetime.today() - timedelta(days = 2000)
        orders = db.session.query(
            Order.platform_id, 
            db.func.year(Order.date),
            db.func.sum(Order.total_price),
        ).filter(Order.platform_id == platform_id).group_by(db.func.year(Order.date),db.func.month(Order.date)).all()
        print("hola, soy una prueba de venta acumulada", orders)
        return orders

        # .filter(Order.platform_id == platform_id).filter(Order.date >= days_ago)
        # sales_result = db.session.query(
        #     Order.platform_id,
        #     db.func.sum(Order.total_price).label('total'))\
        # .filter(Order.platform_id == platform_id).filter(Order.date >= thirty_days_ago, Order.date <= seven_days_ago)\
        # .all()
        # print("TOTAL", sales_result)

        # return sales_result[0][1]

         # rows= db.session.execute(
        #     f"select round(sum(`order`.total_price)) as total, `order`.platform_id from `order` where `order`.id = {platform_id};"
        # ) 
        # for row in rows:
        #     print ("--->", dict(row))
        #     items = row.items()
        #     print("items",items)
        #     total_sales = items[0]
        

class LineItem(db.Model, ModelMixin):
    id= db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)

    def __repr__(self):
        return '<LineItem %r>' % self.product_name

    def serialize(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": self.price,
            "order_id": self.order_id
        }


class Product():
    name = ""
    def __init__(self, name):
        self.name = name
    def serialize(self):
        return {
            "name": self.name
        }

    @staticmethod
    def top_products_for_platform(platform_id, brand_id, period):
        products=[]
        quantity_products= 5
        # period puede ser 'total', 'last_week', 'last_month'
        days_ago = None
        if period == "last_week":
            days_ago = datetime.today() - timedelta(days = 7)
        elif period == "last_month":
            days_ago = datetime.today() - timedelta(days = 30)
        else: 
            days_ago = datetime.today() - timedelta(days = 2000)    
        # ordenes de brand_id y platform_id entre fechas tales
        brand_platform_orders = Order.query.filter_by(
            platform_id=platform_id,
            brand_id=brand_id
        ).filter(Order.date >= days_ago).all()
        print(f"ordenes para marca entre fechas por plataforma {len(brand_platform_orders)}")
        # contar ocurrencias de nombres de producto en los lineitems de estas ordenes
        # { "hamburguesa": 5, "papas fritas": 8, "caramelos": 10 ... }
        counts = {}
        for order in brand_platform_orders:
            order_count = order.get_name_counts()
            for product_name in order_count:
                if product_name in counts:
                    counts[product_name] += order_count[product_name]
                else:
                    counts[product_name] = 1

        # construir lista con los objetos
        count_object_list = []
        for product_name in counts:
            count_object_list.append({
                "name": product_name,
                "counts": counts[product_name]
            })

        # sort de esos objetos a partir del object.count 
        count_object_list.sort(key=lambda count: count["counts"], reverse=True)
        print(f"antes del return {len(count_object_list)} {count_object_list}")
        # return top 5 [ { "name": caramelos, "count": 10 }, ... ]
        return count_object_list[:5]

        # days_ago = None
        # if period == "last_week":
        #     days_ago = datetime.today() - timedelta(days = 7)
        # elif period == "last_month":
        #     days_ago = datetime.today() - timedelta(days = 30)
        # else: 
        #     days_ago = datetime.today() - timedelta(days = 2000)
        # rows= db.session.execute(
        #     # SELECT line_item.product_name FROM line_item 
        #     f"select line_item.product_name from line_item, `order`,platform where `order`.platform_id = platform.id and line_item.order_id =`order`.id and `order`.platform_id = {platform_id} group by product_name order by sum(line_item.quantity) desc limit {quantity_products};"
        # )
        # for row in rows:
        #     product_name = row["product_name"]
        #     product = Product(name=product_name)
        #     products.append(product)
            
        # return products
        