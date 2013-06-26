from flask import Flask
from flask.ext import restful
import mongoengine

from superdesk import resources

mongoengine.connect('superdesk')

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(resources.Items, '/items')

if __name__ == '__main__':
    app.run(debug=True)
