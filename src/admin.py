from flask import Flask
import os
from flask_admin import Admin
from models import db, Enterprise, Brand, Platform, Integration, Clients, Order, LineItem
# Integration, Platform, Midata
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(Enterprise, db.session))
    admin.add_view(ModelView(Brand, db.session))
    admin.add_view(ModelView(Platform, db.session))
    admin.add_view(ModelView(Integration, db.session))
    admin.add_view(ModelView(Clients, db.session))
    admin.add_view(ModelView(Order, db.session))
    # admin.add_view(ModelView(Integration, db.session))
    # admin.add_view(ModelView(Platform, db.session))
    # admin.add_view(ModelView(Midata, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))