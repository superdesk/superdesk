from flask.ext.mail import Message
from superdesk.celery_app import celery
from flask import current_app as app, render_template


@celery.task(bind=True, max_retries=3)
def send_email(self, subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    return app.mail.send(msg)


def send_activate_account_email(doc):
    activate_ttl = app.config['ACTIVATE_ACCOUNT_TOKEN_TIME_TO_LIVE']
    app_name = app.config['APPLICATION_NAME']
    admins = app.config['ADMINS']
    client_url = app.config['CLIENT_URL']
    url = '{}/#/reset-password?token={}'.format(client_url, doc['token'])
    hours = activate_ttl * 24
    text_body = render_template("account_created.txt", app_name=app_name, expires=hours, url=url)
    html_body = render_template("account_created.html", app_name=app_name, expires=hours, url=url)
    send_email.delay(subject='%s account created' % app_name, sender=admins[0], recipients=[doc['email']],
                     text_body=text_body, html_body=html_body)


def send_user_status_changed_email(recipients, is_active):
    status = 'active' if is_active else 'inactive'
    admins = app.config['ADMINS']
    app_name = app.config['APPLICATION_NAME']
    send_email.delay(subject='Your {} account is {}'.format(app_name, status),
                     sender=admins[0],
                     recipients=recipients,
                     text_body=render_template("account_status_changed.txt", app_name=app_name, status=status),
                     html_body=render_template("account_status_changed.html", app_name=app_name, status=status))


def send_reset_password_email(doc):
    token_ttl = app.config['RESET_PASSWORD_TOKEN_TIME_TO_LIVE']
    admins = app.config['ADMINS']
    client_url = app.config['CLIENT_URL']
    app_name = app.config['APPLICATION_NAME']
    url = '{}/#/reset-password?token={}'.format(client_url, doc['token'])
    hours = token_ttl * 24
    text_body = render_template("reset_password.txt", email=doc['email'], expires=hours, url=url, app_name=app_name)
    html_body = render_template("reset_password.html", email=doc['email'], expires=hours, url=url, app_name=app_name)
    send_email.delay(subject='Reset password', sender=admins[0], recipients=[doc['email']],
                     text_body=text_body, html_body=html_body)


def send_user_mentioned_email(recipients, user_name, doc, url):
    print('sending mention email to:', recipients)
    admins = app.config['ADMINS']
    app_name = app.config['APPLICATION_NAME']
    text_body = render_template("user_mention.txt", text=doc['text'], username=user_name, link=url, app_name=app_name)
    html_body = render_template("user_mention.html", text=doc['text'], username=user_name, link=url, app_name=app_name)
    send_email.delay(subject='You were mentioned in a comment by %s' % user_name,
                     sender=admins[0], recipients=recipients,
                     text_body=text_body, html_body=html_body)
