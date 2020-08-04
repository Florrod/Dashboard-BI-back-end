from flask_sqlalchemy import SQLAlchemy
import requests

from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String
from random import randint
from flask_login import UserMixin
from flask import jsonify
from json.decoder import JSONDecodeError

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

class Enterprise(db.Model, ModelMixin):

    id = db.Column(db.Integer, primary_key=True)
    CIF_number = db.Column(db.String(10), unique=True, nullable=True)
    name = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=True) #preguntar como encriptar contraseña a la hora de crearla
    address = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(80),nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, unique=False, nullable=False)
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
            "is_admin": self.is_admin
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
            "orders": list(map(lambda x: x.serialize(), self.orders)), # lo podríamos quitar ya que en este endpoint no nos interesan las orders. Iriamos a orders para verlas
        }
    # def save(self):
    #     db.session.add(self)
    #     db.session.commit
    #     return self

class Platform(db.Model, ModelMixin):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=True)

    integrations = db.relationship('Integration', backref='platform', lazy=True)
    orders = db.relationship('Order', backref='platform', lazy=True)

    def __repr__(self):
        return '<Platform %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "integrations": list(map(lambda x: x.serialize(), self.integrations)),
            "orders": list(map(lambda x: x.serialize(), self.orders))
        }    

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
            "platform_id": self.platform_id
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
            "id": self.id,
            # "email": self.email,
            "phone": self.phone,
            "orders": list(map(lambda x: x.serialize(), self.orders)),
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
        

class Order(db.Model, ModelMixin):
    id= db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(250))
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


    def __repr__(self):
        return '<Order %r>' % self.total_price

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "total_price": self.total_price,
            "lineItems": self.lineItems,
            "brand_id": self.brand_id
        }
    def save(self):
        db.session.add(self)

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
