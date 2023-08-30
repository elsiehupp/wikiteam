""" Provide login functions """

import time

import requests

from wikiteam3.utils.login.api import bot_login, client_login, fetch_login_token
from wikiteam3.utils.login.index import index_login


def uni_login(
    api: str = "",
    index: str = "",
    session: requests.Session = requests.Session(),
    username: str = "",
    password: str = "",
):
    """Try to login to a wiki using various methods.\n
    Return `session` if success, else return `None`.\n
    Try: `cilent login (api) => bot login (api) => index login (index)`"""

    if (not api and not index) or (not username or not password):
        print("uni_login: api or index or username or password is empty")
        return None

    if api:
        print("Trying to log in to the wiki using client_login... (MW 1.27+)")
        if _session := client_login(
            api=api, session=session, username=username, password=password
        ):
            return _session
        time.sleep(5)

        print("Trying to log in to the wiki using bot_login... (MW 1.27+)")
        if _session := bot_login(
            api=api, session=session, username=username, password=password
        ):
            return _session
        time.sleep(5)

    if index:
        print("Trying to log in to the wiki using index_login... (generic)")
        if _session := index_login(
            index=index, session=session, username=username, password=password
        ):
            return _session

    return None
