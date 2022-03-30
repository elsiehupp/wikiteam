import re


class Domain:

    config: dict

    def __init__(self, config: dict):
        self.config = config

    def to_prefix(self):
        """Convert domain name to a valid prefix filename."""

        # At this point, both api and index are supposed to be defined
        domain = ""
        if self.config["api"]:
            domain = self.config["api"]
        elif self.config["index"]:
            domain = self.config["index"]

        domain = domain.lower()
        domain = re.sub(r"(https?://|www\.|/index\.php.*|/api\.php.*)", "", domain)
        domain = re.sub(r"/", "_", domain)
        domain = re.sub(r"\.", "", domain)
        domain = re.sub(r"[^A-Za-z0-9]", "_", domain)

        return domain
