import pytest

from rabbit_consumer.consumer_config import ConsumerConfig

AQ_FIELDS = [
    ("aq_archetype", "AQ_ARCHETYPE"),
    ("aq_domain", "AQ_DOMAIN"),
    ("aq_fqdn", "AQ_FQDN"),
    ("aq_personality", "AQ_PERSONALITY"),
    ("aq_prefix", "AQ_PREFIX"),
    ("aq_url", "AQ_URL"),
]

OPENSTACK_FIELDS = [
    ("openstack_auth_url", "OPENSTACK_AUTH_URL"),
    ("openstack_compute_url", "OPENSTACK_COMPUTE_URL"),
    ("openstack_domain_name", "OPENSTACK_DOMAIN_NAME"),
    ("openstack_project_id", "OPENSTACK_PROJECT_ID"),
    ("openstack_username", "OPENSTACK_USERNAME"),
    ("openstack_password", "OPENSTACK_PASSWORD"),
]

RABBIT_FIELDS = [
    ("rabbit_host", "RABBIT_HOST"),
    ("rabbit_port", "RABBIT_PORT"),
    ("rabbit_username", "RABBIT_USERNAME"),
    ("rabbit_password", "RABBIT_PASSWORD"),
]


@pytest.mark.parametrize(
    "config_name,env_var", AQ_FIELDS + OPENSTACK_FIELDS + RABBIT_FIELDS
)
def test_config_gets_os_env_vars(monkeypatch, config_name, env_var):
    expected = "MOCK_ENV"
    monkeypatch.setenv(env_var, expected)
    assert getattr(ConsumerConfig(), config_name) == expected
