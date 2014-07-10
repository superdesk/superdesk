from flask.ext.mail import Message, Mail
from settings import ADMINS
from flask import current_app as app


def send_reset_password_email(doc):
    send_email('Test email', ADMINS[0], [doc['email']], 'text body', '<p>text html</p>')


def send_email(subject, sender, recipients, text_body, html_body):
    mail = Mail(app)
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
