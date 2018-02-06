from app.models import User, School, Course, FreeInterval
from flask import flash

Schools = ['Tufts University', 'University of Rhode Island']
Courses = ['COMP1','COMP40', 'COMP105', 'CSC106', 'CSC110', 'CSC201', 'CSC211', 'CSC212', 'CSC301', 'CSC305', 'CSC340', 'CSC411', 'CSC412', 'CSC415', 'CSC440']
Mapping = {'Tufts University':['COMP40', 'COMP105','COMP1'], 
           'University of Rhode Island':['CSC106', 'CSC110', 'CSC201', 'CSC211', 'CSC212', 'CSC301', 'CSC305', 'CSC340', 'CSC411', 'CSC412', 'CSC415', 'CSC440']}

ADMINS = ['jack_spam', 'jack_pp', 'jack']

def choices_format(choice):
    return list(map(lambda x: (x,x), choice))

# dangerous waters
def prune_courses(db):
    courses = Course.query.all()
    for c in courses:
        if len(list(c.students)) == 0:
            db.session.delete(c)
    db.session.commit()

def add_or_get(db, name):
    if name in Schools:
        x = School.query.filter_by(name=name)
    else:
        x = Course.query.filter_by(name=name)
    if len(list(x)) == 0:
        if name in Schools:
            temp = School(name=name)
        else:
            temp = Course(name=name)
        db.session.add(temp)
        x = temp
    else:
        try:
            assert(len(list(x)) == 1)
        except Exception:
            raise Exception('Something has gone horribly wrong with the database, an admin has been emailed')
        x = x[0]
    return x

def edit(db, user, form):
    if form.clear.data:
        x = FreeInterval.query.filter_by(author=user)
        for i in x:
            db.session.delete(i)
        flash('Schedule cleared.')
    user.username = form.username.data
    c = add_or_get(db, form.course.data)
    c.institution = user.attending
    user.enrolled = c
    db.session.commit()
    prune_courses(db)

def register(db, user, form):
    s = add_or_get(db, form.school.data)
    c = add_or_get(db, form.course.data)
    try:
        assert(c.name in Mapping[str(s.name)])
    except Exception:
        raise Exception('school course missmatch')
    if c not in s.courses:
        c.institution = s
    user.attending = s
    user.enrolled = c
    db.session.add(user)
    db.session.commit()

def purge(db):
    everyone = User.query.all()
    everyone_else = list(filter(lambda x: str(x.username) not in ADMINS, everyone))
    for e in everyone_else:
        db.session.delete(e)

    all_blocks = FreeInterval.query.all()
    all_schools = School.query.all()
    all_courses = Course.query.all()

    for b in all_blocks:
        db.session.delete(b)
    for c in all_courses:
        db.session.delete(c)
    for s in all_schools:
        db.session.delete(s)
    db.session.commit()