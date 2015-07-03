# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from eve.utils import config

from flask.ext.mail import Message
from settings import OrganizationNameAbbreviation, OrganizationName
from superdesk.celery_app import celery
from flask import current_app as app, render_template, render_template_string


@celery.task(bind=True, max_retries=3, soft_time_limit=10)
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
    subject = render_template("account_created_subject.txt", app_name=app_name)
    text_body = render_template("account_created.txt", app_name=app_name,
                                username=doc['username'], expires=hours, url=url)
    html_body = render_template("account_created.html", app_name=app_name,
                                username=doc['username'], expires=hours, url=url)
    send_email.delay(subject=subject, sender=admins[0], recipients=[doc['email']],
                     text_body=text_body, html_body=html_body)


def send_user_status_changed_email(recipients, status):
    admins = app.config['ADMINS']
    app_name = app.config['APPLICATION_NAME']
    subject = render_template("account_status_changed_subject.txt", app_name=app_name, status=status)
    text_body = render_template("account_status_changed.txt", app_name=app_name, status=status)
    html_body = render_template("account_status_changed.html", app_name=app_name, status=status)
    send_email.delay(subject=subject, sender=admins[0], recipients=recipients,
                     text_body=text_body, html_body=html_body)


def send_reset_password_email(doc):
    token_ttl = app.config['RESET_PASSWORD_TOKEN_TIME_TO_LIVE']
    admins = app.config['ADMINS']
    client_url = app.config['CLIENT_URL']
    app_name = app.config['APPLICATION_NAME']
    url = '{}/#/reset-password?token={}'.format(client_url, doc['token'])
    hours = token_ttl * 24
    subject = render_template("reset_password_subject.txt")
    text_body = render_template("reset_password.txt", email=doc['email'], expires=hours, url=url, app_name=app_name)
    html_body = render_template("reset_password.html", email=doc['email'], expires=hours, url=url, app_name=app_name)
    send_email.delay(subject=subject, sender=admins[0], recipients=[doc['email']],
                     text_body=text_body, html_body=html_body)


def send_user_mentioned_email(recipients, user_name, doc, url):
    print('sending mention email to:', recipients)
    admins = app.config['ADMINS']
    app_name = app.config['APPLICATION_NAME']
    subject = render_template("user_mention_subject.txt", username=user_name)
    text_body = render_template("user_mention.txt", text=doc['text'], username=user_name, link=url, app_name=app_name)
    html_body = render_template("user_mention.html", text=doc['text'], username=user_name, link=url, app_name=app_name)
    send_email.delay(subject=subject, sender=admins[0], recipients=recipients,
                     text_body=text_body, html_body=html_body)


def send_activity_emails(activity, recipients):
    admins = app.config['ADMINS']
    app_name = app.config['APPLICATION_NAME']
    notification = render_template_string(activity.get('message'), **activity.get('data'))
    text_body = render_template("notification.txt", notification=notification, app_name=app_name)
    html_body = render_template("notification.html", notification=notification, app_name=app_name)
    subject = render_template("notification_subject.txt", notification=notification)
    send_email.delay(subject=subject, sender=admins[0], recipients=recipients,
                     text_body=text_body, html_body=html_body)


def send_article_killed_email(article, recipients, trasmitted_at):
    admins = app.config['ADMINS']
    app_name = app.config['APPLICATION_NAME']

    headline = article.get('headline', '')
    trasmitted_at = article[config.LAST_UPDATED] if trasmitted_at is None else trasmitted_at

    text_body = render_template("article_killed.txt", OrganizationNameAbbreviation=OrganizationNameAbbreviation,
                                OrganizationName=OrganizationName, headline=headline, slugline=article.get('slugline'),
                                trasmitted_at=trasmitted_at, app_name=app_name)
    html_body = render_template("article_killed.html", OrganizationNameAbbreviation=OrganizationNameAbbreviation,
                                OrganizationName=OrganizationName, headline=headline, slugline=article.get('slugline'),
                                trasmitted_at=trasmitted_at, app_name=app_name)

    send_email.delay(subject='Transmission from circuit: E_KILL_', sender=admins[0], recipients=recipients,
                     text_body=text_body, html_body=html_body)
