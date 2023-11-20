from pynetbox import api


def api_object(url: str, token: str) -> api:
    return api(url, token)
