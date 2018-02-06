from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail

from flask import flash

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Pairgramming Pro] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))

def send_contact_email(recipients, users, body, schedule):
    send_email('[Pairgramming Pro] New Partner',
                 sender=app.config['ADMINS'][0],
                 recipients=recipients,
                 text_body=render_template('email/contact_email.txt', u1=users[0], u2=users[1], body=body, schedule=schedule),
                 html_body=render_template('email/contact_email.html', u1=users[0], u2=users[1], body=body, schedule=schedule))
