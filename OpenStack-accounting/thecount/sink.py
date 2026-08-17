import logging
from configparser import ConfigParser

import requests
from typing import Optional

logger = logging.getLogger(__name__)

TIMEOUT = (5, 30)  # (connect, read)


class Sink:
    def __init__(self, config_fp: str):
        """ constructor method """
        self._session: Optional[requests.Session] = None
        self._load_config(config_fp)

    def _load_config(self, config_fp: str) -> None:
        """
        helper function to load in thecount config file and extract sink-related config info
        :param config_fp: path to thecount config file
        """
        parser = ConfigParser(interpolation=None)
        if not parser.read(config_fp, encoding="utf-8"):
            raise FileNotFoundError(f"config not found: {config_fp}")
        host = parser.get("sink", "host")
        database = parser.get("sink", "database")
        self.instance = parser.get("sink", "instance")
        self.url = f"http://{host}/write?db={database}&precision=s"
        self._auth = (parser.get("sink", "username"), parser.get("sink", "password"))

    def __enter__(self) -> "Sink":
        """
        Sink is managed via context manager - when context is opened, create and maintain a requests session
        :return: self
        """
        self._session = requests.Session()
        self._session.auth = self._auth
        logger.debug("sink session opened for %s", self.url)
        return self

    def __exit__(self, *exc) -> bool:
        """
        Sink is managed via context manager - when context is closed, close the internal requests session
        """
        if self._session is not None:
            self._session.close()
            self._session = None
        return False

    def write(self, data_string: str) -> None:
        """
        write data to sink influxdb
        :param data_string: string - influx compatible data to pass via POST request to influxdb
        """
        if self._session is None:
            raise RuntimeError("Sink.write() called outside a `with` block")
        if not data_string.strip():
            logger.info("nothing to write")
            return

        response = self._session.post(self.url, data=data_string, timeout=TIMEOUT)
        if not response.ok:
            raise RuntimeError(
                f"influx write failed {response.status_code}: {response.text[:500]}"
            )
        logger.info("wrote %d lines", len(data_string.splitlines()))