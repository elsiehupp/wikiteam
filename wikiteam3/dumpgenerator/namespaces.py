import re

import requests
from delay import delay

# from get_json import get_json


class Namespaces:

    config: dict
    namespace_indices: list
    namespace_dict: dict

    def __init__(self, config: dict):
        self.config = config
        self.namespace_indices = self.config["namespaces"]
        self.namespace_dict = {0: ""}  # main is 0, no prefix
        if self.config["api"]:
            self.fetch_from_api()
        else:
            self.fetch_from_scrape()

    def fetch_from_scrape(self):
        """Hackishly gets the list of namespaces names and ids from the dropdown in the HTML of Special:AllPages"""
        """Function called if no API is available"""
        if self.namespace_indices:
            with requests.Session().post(
                url=self.config["index"],
                params={"title": "Special:Allpages"},
                timeout=30,
            ) as post_response:
                raw = post_response.text
            delay(self.config)

            # [^>]*? to include selected="selected"
            matches = re.compile(
                r'<option [^>]*?value="(?P<namespaceid>\d+)"[^>]*?>(?P<namespacename>[^<]+)</option>'
            ).finditer(raw)
            if "all" in self.namespace_indices:
                self.namespace_indices = []
                for match in matches:
                    self.namespace_indices.append(int(match.group("namespaceid")))
                    self.namespace_dict[int(match.group("namespaceid"))] = match.group(
                        "namespacename"
                    )
            else:
                # check if those namespaces really exist in this wiki
                namespaces_from_query = []
                for match in matches:
                    if int(match.group("namespaceid")) in self.namespace_indices:
                        namespaces_from_query.append(int(match.group("namespaceid")))
                        self.namespace_dict[
                            int(match.group("namespaceid"))
                        ] = match.group("namespacename")
                self.namespace_indices = namespaces_from_query
        else:
            self.namespace_indices = [0]

        self.namespace_indices = list(set(self.namespace_indices))  # uniques
        self.print_namespaces_found()

    def fetch_from_api(self):
        """Uses the API to get the list of namespaces names and ids"""

        if self.namespace_indices:
            with requests.Session().get(
                url=self.config["api"],
                params={
                    "action": "query",
                    "meta": "siteinfo",
                    "siprop": "namespaces",
                    "format": "json",
                },
                timeout=30,
            ) as get_response:
                result = get_response.json()
                delay(self.config)
                try:
                    namespace_query = result["query"]["namespaces"]
                except KeyError:
                    print("Error: could not get namespaces from the API request.")
                    print("HTTP %d" % get_response.status_code)
                    print(get_response.text)
                    self.fetch_from_scrape()
                    return

            if "all" in self.namespace_indices:
                self.namespace_indices = []
                for string_key in namespace_query.keys():
                    if int(string_key) < 0:  # -1: Special, -2: Media, excluding
                        continue
                    self.namespace_indices.append(int(string_key))
                    self.namespace_dict[int(string_key)] = namespace_query[string_key][
                        "*"
                    ]
            else:
                # check if those namespaces really exist in this wiki
                namespaces_from_query = []
                for string_key in namespace_query.keys():
                    int_key = int(string_key)
                    if int_key < 0:  # -1: Special, -2: Media, excluding
                        continue
                    if int_key in self.namespace_indices:
                        namespaces_from_query.append(int_key)
                        self.namespace_dict[int_key] = namespace_query[string_key]["*"]
                self.namespace_indices = namespaces_from_query
        else:
            self.namespace_indices = [0]

        self.namespace_indices = list(set(self.namespace_indices))  # uniques
        self.print_namespaces_found()

    def print_namespaces_found(self):
        print("(%d namespaces found)" % (len(self.namespace_indices)))
