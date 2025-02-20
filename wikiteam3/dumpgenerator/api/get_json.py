import requests


def getJSON(request: requests.Response):
    """Strip Unicode BOM"""
    if request.text.startswith("\ufeff"):
        request.encoding = "utf-8-sig"
    # request.encoding = request.apparent_encoding
    try:
        return request.json()
    except:
        # Maybe an older API version which did not return correct JSON
        return {}
