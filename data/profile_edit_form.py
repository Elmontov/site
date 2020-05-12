from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, IntegerField, DateField, ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, NumberRange
import email_validator

def validate_phone(form, field):
    tel = field.data
    flag = True
    try:
        tel = ''.join(tel.strip().split())
        tel = list(tel)
        if tel[0] == '8':
            tel[0] = '+7'
        tel = ''.join(tel)
        if tel[0:2] != '+7' and tel[0:2] != '+1' and tel[0:3] != '+55' and tel[0:4] != '+359':
            flag = False
            errorMSG = 'Wrong country index'
        if tel[0] == '-' or tel[-1] == '-':
            # print(12)
            raise ValueError
        tel = tel.replace('--', 'kek')
        tel = tel.replace('-', '')
        tel = tel.replace('kek', '--')
        if tel.find('--') != -1:
            # print(13)
            raise ValueError
        tel = list(tel)
        skob = False
        for i in tel:
            if i == '(' and not skob:
                if ')' in tel and tel.index(')') > tel.index(i):
                    tel[tel.index(')')] = ''
                    tel[tel.index(i)] = ''
                    skob = True
                else:
                    # print(14)
                    raise ValueError
            elif '(' not in tel and ')' in tel:
                # print(15)
                raise ValueError
            elif i == '(' and skob:
                # print(17)
                raise ValueError
    except Exception:
        flag = False
        errorMSG = 'Wrong format'

    tel = ''.join(tel)
    if len(tel) != 12 and flag:
        flag = False
        errorMSG = 'Wrong length'

    '''
    if flag:
        flag = False
        errorMSG = 'не определяется оператор сотовой связи'
        op = tel[2:5]
        for i in range(10, 20):
            if op == '9' + str(i):
                flag = True
        for i in range(2, 7):
            if op == '90' + str(i):
                flag = True
        for i in range(80, 90):
            if op == '9' + str(i):
                flag = True
        for i in range(20, 40):
            if op == '9' + str(i):
                flag = True
        for i in range(60, 70):
            if op == '9' + str(i):
                flag = True
    '''
    if not flag:
        raise ValidationError(errorMSG)

class ProfileEditForm(FlaskForm):
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    bd = DateField('Birth day(Y-m-d)')
    address = StringField('Address', validators=[DataRequired()])
    phone_number = StringField('Phone_number', validators=[validate_phone])
    description = StringField('Description', validators=[Length(max=255, message='Description can not exceed 255 symbols')])
    submit = SubmitField('Submit')
