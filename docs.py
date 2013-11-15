
from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs
from app import application

Bootstrap(application)
application.register_blueprint(eve_docs, url_prefix='/docs')

if __name__ == '__main__':
    application.run(debug=True)
