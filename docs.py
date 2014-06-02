
from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs
from app import get_app, setup_amazon

config = setup_amazon({})
app = get_app(config=config)
app.register_blueprint(eve_docs, url_prefix='/docs')
Bootstrap(app)

if __name__ == '__main__':
    app.run(debug=True)
