def get_json(response):
    """Strip Unicode BOM"""
    if response.text.startswith("\ufeff"):
        response.encoding = "utf-8-sig"
    try:
        return response.json()
    except Exception:
        # Maybe an older API version which did not return correct JSON
        return {}
