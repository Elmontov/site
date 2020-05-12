from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class PhotoForm(FlaskForm):
    photo = FileField('Add image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images(png, jpg) only')])
    submit = SubmitField('Submit image')