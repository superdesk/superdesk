
import os

from superdesk import app as application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(debug=True, port=port, host='0.0.0.0')
