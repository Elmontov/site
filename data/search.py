from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, IntegerField, DateField, ValidationError
from wtforms.validators import DataRequired, Length, Email, NumberRange

class SearchForm(FlaskForm):
    search = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Submit')
