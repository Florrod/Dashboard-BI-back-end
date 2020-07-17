from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String
from random import randint
from flask_login import UserMixin

db = SQLAlchemy()

class Enterprise(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    CIF_number = db.Column(db.String(10), unique=True, nullable=True)
    name = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=True) #preguntar como encriptar contraseña a la hora de crearla
    address = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(80),nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, unique=False, nullable=False)
    brand_id = db.relationship('Brand', backref='enterprise', lazy=True)

    # def __init__(self, CIF_number, name, password, address, phone, email, is_active):
    #     self.CIF_number = CIF_number
    #     self.name = name
    #     self.password = password
    #     self.address = address
    #     self.phone = phone
    #     self.email = email
    #     self.is_active = is_active

    def __repr__(self):
        return '<Enterprise %r>' % self.name
    #__repr__ function should return a printable representation of the object, most likely one of the ways possible to create this object

    def save(self):
        db.session.add(self)
        db.session.commit
        return self


    def __init__(self, CIF_number, name, password, address, phone, email, is_active):
        self.CIF_number = CIF_number
        self.name = name
        self.password = password
        self.address = address
        self.phone = phone
        self.email = email
        self.is_active = is_active

    @classmethod
    def get_some_user_id(cls,user_id):
        return cls.query.filter_by(id=user_id).one_or_none()
    
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
            # linea nueva insertada debajo !
            # do not serialize the password, its a security breach
        }

class Brand(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), unique=True, nullable=True)
    logo= db.Column(db.String(120), nullable=True)
    enterprise_to_id = db.Column(db.Integer, db.ForeignKey('enterprise.id'), nullable=False)
    relation_integration = db.relationship('Integration', backref='brand', lazy=True)
    relation_order = db.relationship('Order', backref='brand', lazy=True)

    # def __init__(self, name, logo):
    #     self.name = name
    #     self.logo = logo

    def __repr__(self):
        return '<Brand %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "logo": self.logo,
            "relation_integration": list(map(lambda x: x.serialize(), self.relation_integration)),
            "relation_order": list(map(lambda x: x.serialize(), self.relation_order)),
        }
    # def save(self):
    #     db.session.add(self)
    #     db.session.commit
    #     return self

class Integration(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    API_key= db.Column(db.String(120), nullable=True)
    # deleted = db.Column(db.Boolean(), default=False) #¿Esto está bien? hay que incluirlo en serialize y cómo
    brand_to_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    relation_order = db.relationship('Order', backref='integration', lazy=True)
    
    def __repr__(self):
        return '<Integration %r>' % self.API_key

    def serialize(self):
        return {
            "id": self.id,
            "API_key": self.API_key,
            "relation_order": list(map(lambda x: x.serialize(), self.relation_order)),
            # "deleted": self.deleted,
            # "relation_data": list(map(lambda x: x.serialize(), self.relation_data))
            # if not self.user.deleted else None
        }    

class Platform(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    relation_client_platform = db.relationship('Client_Platform', backref='platform', lazy=True)
    relation_integration = db.relationship('Integration', backref='platform', lazy=True)

    def __repr__(self):
        return '<Platform %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "relation_client_platform": list(map(lambda x: x.serialize(), self.relation_client_platform)),
            "relation_integration": list(map(lambda x: x.serialize(), self.relation_integration)),
            # ¿hay que meter las relaciones?
        }

class Clients(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    relation_order = db.relationship('Order', backref='clients', lazy=True)
    relation_client_platform = db.relationship('Client_Platform', backref='clients', lazy=True)

    #preguntar lo del campo calculado de quantity orders

    def __repr__(self):
        return '<Clients %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "relation_order": list(map(lambda x: x.serialize(), self.relation_order)),
            "relation_client_platform": list(map(lambda x: x.serialize(), self.relation_client_platform)),
            # ¿hay que meter las relaciones?
        }  

class Client_Platform(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Integer) #preguntar si es int o string al ser estrellitas
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)


    def __repr__(self):
        return '<Client_Platform %r>' % self.review


    def serialize(self):
        return {
            "id": self.id,
            "review": self.review,
            # ¿hay que meter las relaciones?
        }

class Order(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(250))
    total_price = db.Column(db.Float)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    integration_id = db.Column(db.Integer, db.ForeignKey('integration.id'), nullable=False)
    relation_lineItem = db.relationship('LineItem', backref='order', lazy=True)

    def __repr__(self):
        return '<Order %r>' % self.total_price

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "total_price": self.total_price,
            "relation_lineItem": self.relation_lineItem
            # ¿hay que meter las relaciones?
        }

class LineItem(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    def __repr__(self):
        return '<LineItem %r>' % self.product_name

    def serialize(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": self.price
            # ¿hay que meter las relaciones?
        }
