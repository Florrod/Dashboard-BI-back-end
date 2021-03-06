from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email

class MyForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(message='Please introduce a valid email')])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('Remember me')