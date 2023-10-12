import pynetbox as nb


class NetboxConnect:
    """
    This class is used to provide the Pynetbox Api object to other classes.
    """

    def __init__(self, url: str, token: str):
        """
        This method initialises NetboxConnect with URL and token
        :param url: Netbox website URL.
        :param token: Netbox authentication token.
        """
        self.url = url
        self.token = token

    def api_object(self):
        """
        This method returns the Pynetbox Api object.
        :return: Returns the Api object
        """
        return nb.api(self.url, self.token)
