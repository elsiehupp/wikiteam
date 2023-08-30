import requests

from wikiteam3.dumpgenerator.config import Config

from .page_xml_api import get_xml_page_with_api
from .page_xml_export import get_xml_page_with_export


# title="", verbose=True
def get_xml_page(config: Config, title: str, verbose: bool, session: requests.Session):
    if config.xmlapiexport:
        return get_xml_page_with_api(
            config=config, title=title, verbose=verbose, session=session
        )
    else:
        return get_xml_page_with_export(
            config=config, title=title, verbose=verbose, session=session
        )
