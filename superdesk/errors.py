from flask import current_app as app

def get_registered_errors(self):
        return {
            'IngestApiError': IngestApiError._codes,
            'IngestFtpError': IngestFtpError._codes,
            'IngestFileError': IngestFileError._codes
        }

class SuperdeskError(Exception):
    _codes = {}

    def __init__(self, code):
        self.code = code
        self.description = self._codes.get(code)
    def __str__(self):
        return repr(self.code)



class SuperdeskApiError(SuperdeskError):
    """Base class for superdesk API."""

    # default error status code
    status_code = 400

    def __init__(self, message=None, status_code=None, payload=None):
        """
        :param message: a human readable error description
        :param status_code: response status code
        :param payload: a dict with request issues
        """
        Exception.__init__(self)
        self.message = message

        if status_code:
            self.status_code = status_code

        if payload:
            self.payload = payload

    def to_dict(self):
        """Create dict for json response."""
        rv = {}
        rv[app.config['STATUS']] = app.config['STATUS_ERR']
        rv['_message'] = self.message or ''
        if hasattr(self, 'payload'):
            rv[app.config['ISSUES']] = self.payload
        return rv


class IdentifierGenerationError(SuperdeskApiError):
    """Exception raised if failed to generate unique_id."""

    status_code = 500
    payload = {'unique_id': 1}
    message = "Failed to generate unique_id"


class InvalidFileType(SuperdeskError):
    """Exception raised when receiving a file type that is not supported."""

    def __init__(self, type=None):
        super().__init__('Invalid file type %s' % type, payload={})




class IngestApiError(SuperdeskError):
    def __init__(self, code):
        self.code = code

    _codes = {
        1101: "Error1 description.",
        1102: "Error1 description",
        1103: "Error1 description",
        1104: "Error1 description"
    }

class IngestFtpError(SuperdeskError):
    def __init__(self, code):
        self.code = code

    _codes = {
        1101: "Error1 description.",
        1102: "Error1 description",
        1103: "Error1 description",
        1104: "Error1 description"
    }

    @classmethod
    def credentialsError(cls):
        return IngestFtpError(1101)


class IngestFileError(SuperdeskError):
    def __init__(self, code):
        self.code = code

    _codes = {
        1101: "Error1 description.",
        1102: "Error1 description",
        1103: "Error1 description",
        1104: "Error1 description"
    }