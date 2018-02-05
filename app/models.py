from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

from time import time
import jwt

from app import app

VALID_COURSES = [11, 12, 13]

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    courses = db.relationship('Course', backref='institution', lazy='dynamic')
    students = db.relationship('User', backref='attending', lazy='dynamic')
    admin_school = db.Column(db.Boolean)

    def __repr__(self):
        return '{}'.format(self.name)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    s_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    students = db.relationship('User', backref='enrolled', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    s_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    c_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    password_hash = db.Column(db.String(128))
    free_times = db.relationship('FreeInterval', backref='author', lazy='dynamic')
    taken = db.Column(db.Boolean)
    partner = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password':self.id, 'exp':time()+expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithm=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class FreeInterval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_day = db.Column(db.String(10))
    start_time = db.Column(db.String(10))
    end_day = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        if self.start_day == self.end_day:
            return '{} from {} to {}.'.format(self.start_day, self.start_time, self.end_time)
        else:
            return '{} at {} to {} at {}.'.format(self.start_day, self.start_time, self.end_day, self.end_time)

    # this doesn't really work, not sure why
    def time_string(self):
        return (str(self.start_day), str(self.start_time), str(self.end_day), str(self.end_time))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
