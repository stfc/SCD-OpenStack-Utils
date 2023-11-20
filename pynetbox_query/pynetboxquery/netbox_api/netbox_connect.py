from pynetbox import api


def api_object(url: str, token: str) -> api:
    """
    This function returns the Pynetbox Api object used to interact with Netbox.
    :param url: The Netbox URL.
    :param token: User Api token.
    :return: The Pynetbox api object.
    """
    return api(url, token)
