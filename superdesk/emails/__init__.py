from flask.ext.mail import Message
from superdesk.celery_app import celery
from flask import current_app as app


@celery.task(bind=True, max_retries=3)
def send_email(self, subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    return app.mail.send(msg)
