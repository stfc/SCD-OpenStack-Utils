import logging
from configparser import ConfigParser
from typing import Optional
 
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
 
logger = logging.getLogger(__name__)
 
TIMEOUT = (5, 30)  # (connect, read) in seconds
DEFAULT_PORT = 8086
 
 
class Sink:
    def __init__(self, config_fp: str):
        """ constructor method """
        self._client: Optional[InfluxDBClient] = None
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
        self._host, _, port = host.partition(":")
        self._port = int(port) if port else DEFAULT_PORT
        self._database = parser.get("sink", "database")
        self.instance = parser.get("sink", "instance")
        self._username = parser.get("sink", "username")
        self._password = parser.get("sink", "password")
 
    def __enter__(self) -> "Sink":
        """
        Sink is managed via context manager - when context is opened, create and maintain an
        influxdb client (which holds an internal requests session)
        :return: self
        """
        self._client = InfluxDBClient(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            database=self._database,
            timeout=TIMEOUT,
        )
        logger.debug(
            "sink client opened for %s:%d/%s", self._host, self._port, self._database
        )
        return self
 
    def __exit__(self, *exc) -> bool:
        """
        Sink is managed via context manager - when context is closed, close the influxdb client
        """
        if self._client is not None:
            self._client.close()
            self._client = None
        return False
 
    def write(self, data_string: str) -> None:
        """
        write data to sink influxdb
        :param data_string: string - influx line protocol data, one measurement per line
        """
        if self._client is None:
            raise RuntimeError("Sink.write() called outside a `with` block")
 
        lines = [line for line in data_string.splitlines() if line.strip()]
        if not lines:
            logger.info("nothing to write")
            return
 
        try:
            self._client.write_points(lines, time_precision="s", protocol="line")
        except (InfluxDBClientError, InfluxDBServerError) as exc:
            raise RuntimeError(f"influx write failed: {exc}") from exc
 
        logger.info("wrote %d lines", len(lines))
