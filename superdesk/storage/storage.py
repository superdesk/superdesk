
import os
import tempfile
from werkzeug import secure_filename
from flask.helpers import send_file


class FileSystemStorage(object):

    def init_app(self, app):
        app.config.setdefault('UPLOAD_FOLDER', tempfile.gettempdir())
        self._root_folder = app.config['UPLOAD_FOLDER']

    def send_file(self, filename, **kwargs):
        return send_file(self._path(filename))

    def save_file(self, filename, fileobj, **kwargs):
        filepath = self._path(filename)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        with open(filepath, 'wb') as f:
            f.write(fileobj.read())
        return os.path.basename(filepath)

    def _path(self, filename):
        return os.path.join(self._root_folder, secure_filename(filename))
