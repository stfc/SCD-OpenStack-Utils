from typing import Dict
from unittest import mock
from unittest.mock import NonCallableMock, patch, call

import pytest

from rabbit_consumer.openstack_api import (
    authenticate,
    update_metadata,
    OpenstackConnection,
    check_machine_exists,
)
from rabbit_consumer.consumer_config import ConsumerConfig


# This is duplicated as it matches a REST API call
# pylint: disable=duplicate-code
def _get_json_auth(rabbit_consumer: ConsumerConfig, project_id) -> Dict:
    return {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": rabbit_consumer.openstack_username,
                        "domain": {"name": rabbit_consumer.openstack_domain_name},
                        "password": rabbit_consumer.openstack_password,
                    }
                },
            },
            "scope": {"project": {"id": project_id}},
        }
    }


@patch("rabbit_consumer.openstack_api.ConsumerConfig")
@patch("rabbit_consumer.openstack_api.openstack.connect")
def test_openstack_connection(mock_connect, mock_config):
    mock_project = NonCallableMock()
    with OpenstackConnection(mock_project) as conn:
        mock_connect.assert_called_once_with(
            auth_url=mock_config.return_value.openstack_auth_url,
            project_name=mock_project,
            username=mock_config.return_value.openstack_username,
            password=mock_config.return_value.openstack_password,
            user_domain_name=mock_config.return_value.openstack_domain_name,
            project_domain_name="default",
        )

        assert conn == mock_connect.return_value
        assert conn.close.call_count == 0

    assert conn.close.call_count == 1


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_check_machine_exists_existing_machine(conn):
    mock_project = NonCallableMock()
    mock_instance = NonCallableMock()

    context = conn.return_value.__enter__.return_value
    context.compute.find_server.return_value = NonCallableMock()
    found = check_machine_exists(mock_project, mock_instance)

    conn.assert_called_once_with(mock_project)
    context.compute.find_server.assert_called_with(mock_instance)
    assert isinstance(found, bool) and found


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_check_machine_exists_deleted_machine(conn):
    mock_project = NonCallableMock()
    mock_instance = NonCallableMock()

    context = conn.return_value.__enter__.return_value
    context.compute.find_server.return_value = None
    found = check_machine_exists(mock_project, mock_instance)

    conn.assert_called_once_with(mock_project)
    context = conn.return_value.__enter__.return_value
    context.compute.find_server.assert_called_with(mock_instance)
    assert isinstance(found, bool) and not found


@patch("rabbit_consumer.openstack_api.ConsumerConfig")
@patch("rabbit_consumer.openstack_api.requests")
def test_authenticate(requests, config):
    project_id = NonCallableMock()
    session = requests.Session.return_value
    session.post.return_value.status_code = 201

    authenticate(project_id)

    requests.Session.assert_called_once()
    session.mount.assert_called_once_with("https://", mock.ANY)
    session.post.assert_called_once()

    args = session.post.call_args
    assert args == call(
        f"{config.return_value.openstack_auth_url}/auth/tokens",
        json=_get_json_auth(config.return_value, project_id),
    )


@patch("rabbit_consumer.openstack_api.requests")
def test_authenticate_throws(requests):
    session = requests.Session.return_value
    session.post.return_value.status_code = 500

    with pytest.raises(ConnectionRefusedError):
        authenticate(NonCallableMock())


@patch("rabbit_consumer.openstack_api.ConsumerConfig")
@patch("rabbit_consumer.openstack_api.requests")
@patch("rabbit_consumer.openstack_api.authenticate")
def test_update_metadata(auth, requests, config):
    project_id, instance_id = "mock_project", "mock_instance"
    metadata = NonCallableMock()
    session = requests.Session.return_value
    session.post.return_value.status_code = 200

    update_metadata(project_id, instance_id, metadata)

    session.mount.assert_called_once_with("https://", mock.ANY)
    auth.assert_called_once_with(project_id)
    session.post.assert_called_once()

    assert session.post.call_args == call(
        f"{config.return_value.openstack_compute_url}"
        f"/{project_id}/servers/{instance_id}/metadata",
        headers={"Content-type": "application/json", "X-Auth-Token": auth.return_value},
        json={"metadata": metadata},
    )


@patch("rabbit_consumer.openstack_api.authenticate")
@patch("rabbit_consumer.openstack_api.requests")
def test_update_metadata_throws_exception(_, requests):
    session = requests.Session.return_value
    session.post.return_value.status_code = 500

    with pytest.raises(ConnectionAbortedError):
        update_metadata(NonCallableMock(), NonCallableMock(), NonCallableMock())
