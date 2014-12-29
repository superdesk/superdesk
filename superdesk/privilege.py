"""Privileges registry."""

_privileges = {}
_intrinsic_privileges = {}


class PrivilegeNameError(Exception):
    pass


def privilege(**kwargs):
    """Register privilege.

    Privilege name must not contain "."

    Privilege properties:
    - name
    - label
    - description
    - category
    """
    if '.' in kwargs['name']:
        raise PrivilegeNameError('"." is not supported in privilege name "%s"' % kwargs['name'])
    _privileges[kwargs['name']] = kwargs


def get_privilege_list():
    """Get list of all registered privileges."""
    return [v for v in _privileges.values()]


def intrinsic_privilege(resource_name, method=[]):
    """
    Registers intrinsic privileges.
    """

    _intrinsic_privileges[resource_name] = method


def get_intrinsic_privileges():
    """Get list of all registered intrinsic privileges."""

    return _intrinsic_privileges
