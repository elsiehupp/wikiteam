import re

from wikiteam3.dumpgenerator.config import Config


def domain2prefix(config: Config = None, session=None):
    """Convert domain name to a valid prefix filename."""

    # At this point, both api and index are supposed to be defined
    domain = ""
    if config.api:
        domain = config.api
    elif config.index:
        domain = config.index

    domain = domain.lower()
    domain = re.sub(r"(https?://|www\.|/index\.php.*|/api\.php.*)", "", domain)
    domain = re.sub(r"/.*", "", domain)
    # domain = re.sub(r"\.", "", domain)
    domain = re.sub(r"[^.A-Za-z0-9]", "_", domain)

    return domain
~~~~~~~~~~~~~~
import re

file_path =

# Read the file
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

# Count occurrences using regex
title_count = len(re.findall(r"<title.*?>", file_content))
page_open_count = len(re.findall(r"<page.*?>", file_content))
page_close_count = len(re.findall(r"</page>", file_content))
revision_open_count = len(re.findall(r"<revision.*?>", file_content))
revision_close_count = len(re.findall(r"</revision>", file_content))

# Check conditions
if (
    title_count == page_open_count == page_close_count
    and revision_open_count == revision_close_count
    and file_content.strip().endswith('</mediawiki>')
):
    xmlokay = "true"
else:
    xmlokay = "false"

Return