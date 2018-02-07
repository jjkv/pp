# NEEDSMERGE

from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddForm, ResetPasswordRequestForm, ResetPasswordForm, ContactForm

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, School, Course, FreeInterval, VALID_COURSES
from app.email import send_password_reset_email, send_contact_email

import functools

import app.intersections as IN
import app.timeparsing as TP
import app.db_manip as DM
#from scripts import ut as UT

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    addform = AddForm(smins='00', emins='00')
    if addform.validate_on_submit() and addform.submit.data:
        sd = str(addform.sday.data)
        st = TP.form_data_to_timestr(addform.shours.data, addform.smins.data)
        et = TP.form_data_to_timestr(addform.ehours.data, addform.emins.data)

        try:
            ed = TP.end_day_validate(sd, st, et)
        except Exception as inst:
            flash(inst.args)
            return redirect(url_for('index'))
        sd, st, ed, et = TP.sanitize_timestr(sd, st, ed, et)

        fi = FreeInterval(author=current_user,
                          start_day=sd,
                          start_time=st,
                          end_day=ed,
                          end_time=et)
        db.session.add(fi)
        db.session.commit()
        flash('time block added, thanks')
        if sd != ed:
            flash('note: time block extends to next day, from '+sd+' to '+ed)
        return redirect(url_for('index'))

    schedule = FreeInterval.query.filter_by(author=current_user)
    if list(schedule):
        return render_template('index.html', title='Home', form=addform, schedule=schedule)
    else:
        return render_template('index.html', title='Home', form=addform)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        try:
            DM.register(db, user, form)
            flash('Congratulations, you are now a registered user!')
        except Exception as inst:
            flash(functools.reduce(lambda x, y: x+y, inst.args, "error(s) in registration: ")+".")
            return redirect(url_for('register'))
        return redirect(url_for('login'))
    flash("Don't see your school here and want to use this website? Email us at pairgramming.pro@gmail.com")
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    schedule = schedule = FreeInterval.query.filter_by(author=user)

    if user.username == current_user.username and str(current_user.username) in DM.ADMINS:
        return render_template('user.html', user=user, admin=True, schedule=schedule)
    else:
        return render_template('user.html', user=user, schedule=schedule)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.username not in DM.ADMINS:
        flash('Access denied!')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin.html', title='Admin Panel', users=users)


@app.route('/purge', methods=['GET', 'POST'])
@login_required
def purge():
    if current_user.username not in DM.ADMINS:
        flash('Access denied!')
        return redirect(url_for('index'))
    try:
        DM.purge(db)
    except Exception as inst:
        flash(functools.reduce(lambda x, y: x+y, inst.args, "error(s) in purge: ")+".")
    flash('Purge complete, all schedules cleared, all non admin users removed')
    return redirect(url_for('admin'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.attending:
        form = EditProfileForm(current_user.username, current_user.attending.name, taken=current_user.taken)
    else:
        form = EditProfileForm(current_user.username, taken=current_user.taken)
    if form.validate_on_submit():
        DM.edit(db, current_user, form)
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        if form.password.data == "password":
            flash('password? really?')
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/request_partner', methods=['GET', 'POST'])
@login_required
def request_partner():
    old_partner = ""
    if current_user.taken:
        old_partner = current_user.partner_username()
        current_user.decouple()
        db.session.commit()
        assert(current_user.taken == False)
        #flash('You already have a partner, please check your email! If this is not the case, or you would like to request a new partner, go to Profile -> Edit Profile and verify that you do not have a partner.')
    compatible_users = list(filter(lambda x: x.username != current_user.username and x.taken != True and x.username != old_partner, 
                              User.query.filter_by(enrolled=current_user.enrolled)))
    if not compatible_users:
        flash('Sorry, there are no compatible '+str(current_user.enrolled)+' student users right now, please try again later or add more time to your work schedule.')
        return redirect(url_for('index'))
    elif len(list(compatible_users)) < 1:
        flash('Sorry, there are no compatible '+str(current_user.enrolled)+' student users right now, please try again later or add more time to your work schedule.')
        return redirect(url_for('index'))

    my_intervals = list(map(lambda x: tuple(map(str, [x.start_day, 
                                                 x.start_time, 
                                                 x.end_day, 
                                                 x.end_time])), 
                       current_user.free_times))

    match_list = []
    for you in compatible_users:
        your_intervals = list(map(lambda x: tuple(map(str, [x.start_day, 
                                                       x.start_time, 
                                                       x.end_day, 
                                                       x.end_time])),
                                    you.free_times))        
        try:
            mins1, mins2      = TP.timestr_to_minutes(my_intervals), TP.timestr_to_minutes(your_intervals)
            tree1, tree2      = IN.list_to_intervaltree(mins1), IN.list_to_intervaltree(mins2)
            intertree         = IN.intervaltree_intersections(tree1, tree2)
            interlist         = IN.condense_intervals(intertree)
            newtree           = IN.intervals_to_tree(interlist)
            intersection_mins = IN.tree_to_list(newtree)
            free_inter_ts     = TP.minutes_to_timestr(intersection_mins)
            combined_ft       = IN.total_free_time(intersection_mins)

            if combined_ft > 0:
                match_list.append((you, free_inter_ts, combined_ft))
        except Exception as inst:
            flash(functools.reduce(lambda x, y: x+y, inst.args, 
                         "error(s) in partner request: ")+".")
            flash('Check that your schedule is correctly formatted and try again.')
            return redirect(url_for('index'))

    match_list = sorted(match_list, key=lambda x: x[2], reverse=True)

    if len(match_list) > 0:
        best = match_list[0]
        overlap = list(map(lambda x: ""+(x[0])+" at "+(x[1])+" until "+(x[2])+" at "+(x[3])+".", best[1]))
        db.session.commit()
        return render_template('request_partner.html', 
                                title='Request Partner', 
                                partner=best[0], 
                                schedule=overlap, 
                                ft=best[2],
                                link=str(best[0].username),
                                rest=list(map(lambda x: (x[0].username, x[1], x[2]), match_list[1:])))
    else:
        flash('Sorry, we could not find you a match! Please try again later.')
        return redirect(url_for('index'))

# this is so hacky omg i hate it
@app.route('/other_matches/<matches>', methods=['GET', 'POST'])
@login_required
def other_matches(matches):
    if len(str(matches)) <= 2:
        flash('no other matches right now')
        return redirect(url_for('index'))
    temp = matches.replace('[','').replace(']','').replace('(','').replace(')','').replace("'",'').replace(' ','').split(',')
    chunks = list(zip(*[iter(temp)]*6))

    temp2 = []
    for c in chunks[:5]:
        name = str(c[0])
        flash(name)
        user = User.query.filter_by(username=name).first()
        schedule = str(c[1])+" at "+str(c[2])+" until "+str(c[3])+" at "+str(c[4])+"."
        total = str(c[5])
        temp2.append((user, schedule, total))
    return render_template('other_matches.html', matches=temp2)

@app.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    x = FreeInterval.query.filter_by(id=str(id)).first_or_404()
    db.session.delete(x)
    flash('Deletion successful!')
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/contact/<total>/<schedule>/<partner>', methods=['GET', 'POST'])
@login_required
def contact(schedule, total, partner):
    u = User.query.get(partner)
    if not u:
        flash('Sorry! Something went wrong')
        redirect(url_for('index'))
    form = ContactForm(recipients=str(current_user.email)+', '+str(u.email), body=str("Hi "+str(u.username)+"!"))
    if form.validate_on_submit():
        rs      = [str(current_user.email), str(u.email)]
        others  = list(map(lambda x: str(x), form.recipients.data.replace(' ','').split(',')))
        rs      = list(set(rs + others))
        send_contact_email(rs, (current_user.username, u.username), form.body.data, schedule)
        flash('You and your new partner have been emailed, please check your inbox.')
        current_user.set_partner(u)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('contact.html', form=form)

@app.route('/stats', methods=['POST', 'GET'])
def stats():
    schools = School.query.all()
    courses = list(filter(lambda x: x.name != 'COMP1', list(Course.query.all())))
    users   = User.query.all()
    return render_template('stats.html', title='Stats', schools=schools, cn_pair=list(map(lambda x: (x, len(list(x.students))), list(courses))), users=users)
