
from app import get_app, setup_amazon

config = setup_amazon({})
application = get_app(config=config)
