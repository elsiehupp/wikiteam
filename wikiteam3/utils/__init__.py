from .domain import domain_2_prefix
from .login.login import (
    bot_login,
    client_login,
    fetch_login_token,
    index_login,
    uni_login,
)

# from .monkey_patch import mod_requests_text
from .uprint import uprint
from .user_agent import get_user_agent
from .util import clean_html, clean_xml, remove_ip, sha1_file, undo_html_entities
from .wiki_avoid import avoid_wikimedia_projects
