import configparser
import logging
import os
from datetime import datetime
from typing import Optional, Dict

import sqlalchemy
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

QUERY = sqlalchemy.text("CALL get_accounting_data(:start, :end)")


class Source:
    """
    Reads accounting data from the OpenStack MySQL databases.

    Engines are created lazily on first use of each database and reused for
    every subsequent window, then disposed when the block exits.
    """

    def __init__(self, config_fp: str):
        """constructor class"""
        self._engines: Optional[Dict[str, sqlalchemy.Engine]] = None
        self._load_config(config_fp)

    def _load_config(self, config_fp: str) -> None:
        """
        Helper function to read in thecount config file and pre-set environment variables
        to setup a Source object.

        Constructs a connection string to connect to source DB.

        Done in __init__ so issues with the config path and environment variables fails at startup
        rather than on the first window

        :param config_fp: path to config file
        """

        def require_env(name: str) -> str:
            """
            helper to load in environment variables
            :param name: environment variable name
            :return: environment variable value
            """
            value = os.getenv(name)
            if not value:
                raise ValueError(f"{name}: openstack db environment variable not set")
            return value

        parser = configparser.ConfigParser()
        if not parser.read(config_fp, encoding="utf-8"):
            raise FileNotFoundError(f"config not found: {config_fp}")
        port = parser.getint("source", "port")

        username = require_env("THE_COUNT_SOURCE_USERNAME")
        password = require_env("THE_COUNT_SOURCE_PASSWORD")
        host = require_env("THE_COUNT_SOURCE_HOST")

        self.conn_string = f"mysql+pymysql://{username}:{password}@{host}:{port}"

    def __enter__(self) -> "Source":
        """
        Source is managed via context manager, when context is opened, set engines to empty dict {}
        forcing a new sqlalchemy engine to be instantiated and stored for each DB opened
        :return: self
        """
        if self._engines is not None:
            raise RuntimeError("Source is already open")
        self._engines = {}
        return self

    def __exit__(self, *exc) -> bool:
        """
        Source is managed via context manager, when context is closed, disposes of any instantiated engines
        """
        for database, engine in self._engines.items():
            logger.debug("disposing engine for %s", database)
            engine.dispose()
        self._engines = None
        return False

    def _engine(self, database: str) -> sqlalchemy.Engine:
        """
        Engines live for the whole run, so connections will sit idle between
        windows. pool_pre_ping revives ones the server has dropped;
        pool_recycle retires them before MySQL's wait_timeout does.

        instantiating and maintaining engines reduces operational overhead and memory
        needed for continuous processes
        :param database: database to open from source sql db
        """
        if database not in self._engines:
            logger.debug("creating engine for %s", database)
            self._engines[database] = sqlalchemy.create_engine(
                f"{self.conn_string}/{database}",
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=1,
                max_overflow=0,
            )
        return self._engines[database]

    def fetch(
        self, database: str, start_time: datetime, end_time: datetime
    ) -> list[dict]:
        """
        Call the accounting sql procedure for a single interval.

        :param database: database to query, e.g. "nova"
        :param start_time: interval start time
        :param end_time: interval end time
        :returns: results as list of dicts
        """
        if self._engines is None:
            raise RuntimeError("Source.fetch() called outside a `with` block")

        start = start_time.strftime("%Y-%m-%d %H:%M")
        end = end_time.strftime("%Y-%m-%d %H:%M")
        logger.debug("get_accounting_data(%s, %s) on %s", start, end, database)

        with Session(self._engine(database)) as session:
            result = session.execute(QUERY, {"start": start, "end": end})
            return [dict(row) for row in result.mappings()]
