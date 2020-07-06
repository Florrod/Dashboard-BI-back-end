from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String

db = SQLAlchemy()

class Enterprise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    CIF_number = db.Column(db.String(10), unique=True, nullable=True)
    name = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(80),nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    relation_brand = relationship('Brand')
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    # def __repr__(self):
    #     return '<User %r>' % self.userename

    def serialize(self):
        return {
            "id": self.id,
            "CIF_number": self.CIF_number,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email

            # do not serialize the password, its a security breach
        }

class Brand(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), unique=True, nullable=True)
    logo= db.Column(db.String(120), nullable=True)
    enterprise_to_id= db.Column(db.Integer, db.ForeignKey('Enterprise.id')) #¿Esto está bien?
    relation_brand= relationship('Integration')
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "logo": self.logo,
            "address": self.address
        }

class Integration(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    API_key= db.Column(db.String(120), nullable=True)
    deleted = db.Column(db.Boolean(), default=False) #¿Esto está bien? hay que incluirlo en serialize y cómo
    platform_id = db.Column(db.Integer, db.ForeignKey('Platform.id'))
    brand_to_id = db.Column(db.Integer, db.ForeignKey('Brand.id'))
    relation_data = relationship('Data')

    def serialize(self):
        return {
            "id": self.id,
            "API_key": self.API_key,
            "deleted": self.deleted
            # if not self.user.deleted else None
        }

class Platform(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    relation_integration = relationship('Integration')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            # ¿hay que meter las relaciones?
        }

class Data(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.String(250))
    brand_to_id = db.Column(Integer, db.ForeignKey('Brand.id'))
    integration_to_id = db.Column(Integer, db.ForeignKey('Integration.id'))

    def serialize(self):
        return {
            "id": self.id,
            "detail": self.name,
            # ¿hay que meter las relaciones?
        }









