import logging
import etcd3

from rabbit_consumer.consumer_config import ConsumerConfig

logger = logging.getLogger(__name__)

class EtcdClient:
    """
    Wrapper for etcd client.
    """

    def __init__(self):
        self.client = None

    def __enter__(self):
        self.client = etcd3.client(
            host=ConsumerConfig().etcd_host,
            port=int(ConsumerConfig().etcd_port),
            user=ConsumerConfig().etcd_username,
            password=ConsumerConfig().etcd_password,
        )
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


def etcd_put(key: str, value: str):
    """
    Put value into etcd
    """
    with EtcdClient() as client:
        client.put(key, value)


def etcd_get(key: str):
    """
    Get value from etcd
    """
    with EtcdClient() as client:
        return client.get(key)
