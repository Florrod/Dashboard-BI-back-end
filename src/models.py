from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String
from random import randint
from flask_login import UserMixin
from flask import jsonify

db = SQLAlchemy()

class DatabaseManager():
    @staticmethod
    def commit():
        db.session.commit()


class Enterprise(db.Model, UserMixin):

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

class Brand(db.Model):
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

class Platform(db.Model):
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

class Integration(db.Model):
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
            "orders": list(map(lambda x: x.serialize(), self.orders))
        }    

    def getData(self, from_date=""): 

# import requests 
# r = requests.get(url = URL, params = PARAMS) 
  
# extracting data in json format 
# data = r.json() 
        data = {
            "orders":[
                {
                    "id": 1,
                    "lines":[
                        {
                            "id": 1,
                            "name": "Producto 1",
                            "price": 10,
                            "quantity": 1
                        }
                    ],
                    "client":{
                        "name": "Juan",
                        "email": "juan@gmail.com"
                    }
                }
            ]
        }

        return data

class Clients(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    orders_count = db.Column(db.Integer)

    orders = db.relationship('Order', backref='clients', lazy=True)

    #preguntar lo del campo calculado de quantity orders

    def __repr__(self):
        return '<Clients %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "orders": list(map(lambda x: x.serialize(), self.orders))
        } 

    def save(self):
        db.session.add(self) 

    @classmethod
    def getWithEmail(cls, email):
        return db.session.query(cls).filter_by(email=email).one_or_none()
    # ¿classmethod?

class Order(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(250))
    total_price = db.Column(db.Float)
    review = db.Column(db.Float)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    integration_id= db.Column(db.Integer, db.ForeignKey('integration.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    lineItems = db.relationship('LineItem', cascade="all,delete", backref='order', lazy=True)

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

class LineItem(db.Model):
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
