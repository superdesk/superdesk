"""
Superdesk server app
"""

import flask
from flask.ext import restful
import mongoengine

from superdesk import resources

def connect_db():
    mongoengine.connect(app.config.get('DB_NAME', 'superdesk'))

app = flask.Flask(__name__)
app.config.from_object('settings')

api = restful.Api(app)
api.add_resource(resources.Items, '/items/')

@app.before_request
def before_request():
    connect_db()

if __name__ == '__main__':
    app.run(debug=True)
