"""
Superdesk server app
"""

import flask
from flask.ext import restful
import mongoengine

from superdesk import resources

def connect_db():
    mongoengine.connect(app.config.get('DB_NAME', 'superdesk'))

app = flask.Flask('superdesk')
app.config.from_object('settings')

@app.before_request
def before_request():
    connect_db()

api = restful.Api(app)
api.add_resource(resources.Auth, '/auth')
api.add_resource(resources.Items, '/items/')

if __name__ == '__main__':
    app.run(debug=True)
