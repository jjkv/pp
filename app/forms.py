from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, FreeInterval

import functools

from flask import flash

import app.timeparsing as TP
import app.db_manip as DM

class Choices:
    days = [('monday','Monday'),('tuesday','Tuesday'),('wednesday','Wednesday'),('thursday','Thursday'),('friday','Friday'),('saturday',"Saturday"),('sunday','Sunday')]
    hours = [('00','12AM'),('1','01AM'),('2','02AM'),('3','03AM'),('4','04AM'),('5','05AM'),('6','06AM'),('7','07AM'),('8','08AM'),('9','09AM'),('10','10AM'),('11','11AM'),('12','12PM'),('13','01PM'),('14','02PM'),('15','03PM'),('16','04PM'),('17','05PM'),('18','06PM'),('19','07PM'),('20','08PM'),('21','09PM'),('22','10PM'),('23','11PM')]
    schools = DM.Schools
    courses = DM.Courses

# global helper that turns a collection of errors into an error string
def error_str(error_list, label="error(s): "):
    return functools.reduce(lambda x, y: x + y, error_list, label)

# i made some bad design choices
# first refactor will be creating a module to sanitize the input,
# used by both forms and time_parsing
# right now the code is redundant and not well abstracted

# 1/19/18 sanitization has been added, but not yet tested

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

'''
def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if '.' not in str(email.data) and 'jack' not in str(email.data) and 'pair' not in str(email.data):
            raise ValidationError('Invalid email address, please try again.')
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_password(self, password):
        if 'pass' in str(password.data):
            raise ValidationError('You can do better than that, please try a different password')
        elif len(str(password.data)) < 8:
            raise ValidationError('Password should be at least 8 characters, please try again')
'''

class RegistrationForm(FlaskForm):
    username = StringField('Username (preferred name would be ideal: first_last)', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    course = SelectField('Course', choices=DM.choices_format(Choices.courses), validators=[DataRequired()])
    school = SelectField('School', choices=DM.choices_format(Choices.schools), validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if '.' not in str(email.data) and 'jack' not in str(email.data) and 'pair' not in str(email.data):
            raise ValidationError('Invalid email address, please try again.')
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_password(self, password):
        if 'pass' in str(password.data):
            raise ValidationError('You can do better than that, please try a different password')
        elif len(str(password.data)) < 8:
            raise ValidationError('Password should be at least 8 characters, please try again')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    course = SelectField('Course', choices=DM.choices_format(Choices.courses), validators=[DataRequired()])
    clear = BooleanField('Clear your schedule on submit.')
    taken = BooleanField('I have a partner (I will not be able to be paired with other users).')
    submit = SubmitField('Submit')

    def __init__(self, original_username, original_school, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_school = original_school

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please choose a different username.')

    def validate_course(self, course):
        if course.data not in DM.Mapping[self.original_school]:
            raise ValidationError('The course you have selected is not part of this school')

class AddForm(FlaskForm):
    sday = SelectField("Day", choices=Choices.days, validators=[DataRequired()])
    shours = SelectField("Start", choices=Choices.hours, validators=[DataRequired()])
    smins = StringField('Minutes', validators=[DataRequired()])
    ehours = SelectField("End", choices=Choices.hours, validators=[DataRequired()])
    emins = StringField('Minutes', validators=[DataRequired()])
    #next_day = BooleanField('Is this the next day?')
    submit = SubmitField('Add time block')

    def validate_smins(self, smins):
        try:
            TP.min_str(smins.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "errors(s) in minute submission: "))

    def validate_emins(self, emins):
        try:
            TP.min_str(emins.data)
        except Exception as inst:
            raise ValidationError(error_str(inst.args, "errors(s) in minute submission: "))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ContactForm(FlaskForm):
    recipients = StringField('Email recipients: ', validators=[DataRequired()])
    body = TextAreaField('Say something to your partner:', validators=[DataRequired()])
    agree = BooleanField('I agree to this partnership (you will not be paired with other users while this partnership persists)')
    submit = SubmitField('Send')

    def validate_agree(self, agree):
        if agree.data != True:
            raise ValidationError('You must agree before sending this email.')
