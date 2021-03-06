from __future__ import unicode_literals

import getpass
import logging
import sys

from six.moves import input, range

from rbtools.api.errors import AuthorizationError
from rbtools.commands import CommandError


def get_authenticated_session(api_client, api_root, auth_required=False,
                              session=None, num_retries=3):
    """Return an authenticated session.

    None will be returned if the user is not authenticated, unless the
    'auth_required' parameter is True, in which case the user will be prompted
    to login.
    """
    if not session:
        session = api_root.get_session(expand='user')

    if not session.authenticated:
        if not auth_required:
            return None

        logging.info('Please log in to the Review Board server at %s',
                     api_client.domain)

        for i in range(num_retries):
            sys.stderr.write('Username: ')
            username = input()
            password = getpass.getpass(b'Password: ')
            api_client.login(username, password)

            try:
                session = session.get_self()
                break
            except AuthorizationError:
                sys.stderr.write('\n')

                if i < num_retries - 1:
                    logging.error('The username or password was incorrect. '
                                  'Please try again.')
                else:
                    raise CommandError('Unable to log in to Review Board.')

    return session


def get_user(api_client, api_root, auth_required=False):
    """Return the user resource for the current session."""
    session = get_authenticated_session(api_client, api_root, auth_required)

    if session:
        return session.user

    return None


def get_username(api_client, api_root, auth_required=False):
    """Return the username for the current session."""
    user = get_user(api_client, api_root, auth_required)

    if user:
        return user.username

    return None
