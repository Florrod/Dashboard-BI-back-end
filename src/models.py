from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String
db = SQLAlchemy()

class Midata(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.String(250))
    brand_to_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    integration_to_id = db.Column(db.Integer, db.ForeignKey('integration.id'))
    def __ref__(self):
        return f'<Midata {self.id}>'
    def serialize(self):
        return {
            "id": self.id,
            "detail": self.detail,
            # ¿hay que meter las relaciones?
        }
class Integration(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    API_key= db.Column(db.String(120), nullable=True)
    deleted = db.Column(db.Boolean(), default=False) #¿Esto está bien? hay que incluirlo en serialize y cómo
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))
    brand_to_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    relation_data = db.relationship("Midata", lazy=True)
    def __ref__(self):
        return f'<Integration {self.id}>'
    def serialize(self):
        return {
            "id": self.id,
            "API_key": self.API_key,
            "deleted": self.deleted,
            "relation_data": list(map(lambda x: x.serialize(), self.relation_data))
            # if not self.user.deleted else None
        }
class Brand(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), unique=True, nullable=True)
    logo= db.Column(db.String(120), nullable=True)
    enterprise_to_id = db.Column(db.Integer, db.ForeignKey('enterprise.id')) #¿Esto está bien?
    # relation_brand= relationship('Integration')
    relation_integration = db.relationship('Integration', lazy=True)
    def __ref__(self):
        return f'<Brand {self.name}>'
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "logo": self.logo,
            "address": self.address,
            "relation_integration": list(map(lambda x: x.serialize(), self.relation_integration))
        }
class Enterprise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    CIF_number = db.Column(db.String(10), unique=True, nullable=True)
    name = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(80),nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    # relation_brand = relationship('Brand')
    relation_brand = db.relationship("Brand", lazy=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
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
            # linea nueva insertada debajo !
            "relation_brand": list(map(lambda x: x.serialize(), self.relation_brand))
            # do not serialize the password, its a security breach
        }
class Platform(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    relation_integration = db.relationship('Integration', lazy=True)
    def __ref__(self):
        return f'<Platform {self.name}>'
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "relation_integration": list(map(lambda x: x.serialize(), self.relation_integration))
            # ¿hay que meter las relaciones?
        }