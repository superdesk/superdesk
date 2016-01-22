
from app import get_app
from superdesk.factory import get_manager

if __name__ == '__main__':
	get_manager(get_app()).run()
