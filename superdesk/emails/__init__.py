from flask.ext.mail import Message
from superdesk.celery_app import celery
from settings import ADMINS, RESET_PASSWORD_TOKEN_TIME_TO_LIVE as expiration_time
from flask import render_template, current_app as app


def send_reset_password_email(doc):
    send_email.delay(subject='Reset password',
                     sender=ADMINS[0],
                     recipients=[doc['email']],
                     text_body=render_template("reset_password.txt", user=doc, expires=expiration_time),
                     html_body=render_template("reset_password.html", user=doc, expires=expiration_time))


@celery.task(bind=True, max_retries=3)
def send_email(self, subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    return app.mail.send(msg)
