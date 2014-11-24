"""Privileges registry."""

_privileges = {}


def privilege(**kwargs):
    """Register privilege.

    Privilege properties:
    - name
    - label
    - description
    - category
    """
    kwargs['name'] = kwargs['name'].replace('.', ':')
    _privileges[kwargs['name']] = kwargs


def get_privilege_list():
    """Get list of all registered privileges."""
    return [v for v in _privileges.values()]
