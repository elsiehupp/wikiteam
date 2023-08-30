""" Always available login methods.(mw 1.16-1.39)
    Even oler versions of MW may work, but not tested. """

from typing import Optional

import lxml.html
import requests


def index_login(
    index: str, session: requests.Session, username: str, password: str
) -> Optional[requests.Session]:
    """Try to login to a wiki using username and password through `Special:UserLogin`.
    (tested on MW 1.16...1.39)"""
    wp_edit_token = None
    wp_login_token = None

    params = {
        "title": "Special:UserLogin",
    }
    r = session.get(index, allow_redirects=True, params=params)

    # Sample r.text:
    # MW 1.16: <input type="hidden" name="wp_login_token" value="adf5ed40243e9e5db368808b27dc289c" />
    # MW 1.39: <input name="wp_login_token" type="hidden" value="ad43f6cc89ef50ac3dbd6d03b56aedca63ec4c90+\"/>
    html = lxml.html.fromstring(r.text)
    if "wp_login_token" in r.text:
        wp_login_token = html.xpath('//input[@name="wp_login_token"]/@value')[0]

    # Sample r.text:
    # MW 1.16: None
    # MW 1.39: <input id="wp_edit_token" type="hidden" value="+\" name="wp_edit_token"/>
    if "wp_edit_token" in r.text:
        wp_edit_token = html.xpath('//input[@name="wp_edit_token"]/@value')[0]
        print("index login: wp_edit_token found.")

    data = {
        "wpName": username,  # required
        "wpPassword": password,  # required
        "wpLoginattempt": "Log in",  # required
        "wpLoginToken": wp_login_token,  # required
        "wpRemember": "1",  # 0: not remember, 1: remember
        "wpEditToken": wp_edit_token,  # introduced before MW 1.27, not sure whether it's required.
        "authAction": "login",  # introduced before MW 1.39.
        "title": "Special:UserLogin",  # introduced before MW 1.39.
        "force": "",  # introduced before MW 1.39, empty string is OK.
    }
    r = session.post(index, allow_redirects=False, params=params, data=data)
    if r.status_code == 302:
        print("index login: Success! Welcome, ", username, "!")
        return session
    else:
        print(
            "index login: Oops! Something went wrong -- ",
            r.status_code,
            "wp_login_token: ",
            wp_login_token,
            "wp_edit_token: ",
            wp_edit_token,
        )
        return None
