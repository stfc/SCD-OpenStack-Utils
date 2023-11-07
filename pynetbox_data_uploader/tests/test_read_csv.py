from pytest import fixture, raises
from lib.user_methods.csv_to_netbox import CsvToNetbox


@fixture(name="instance")
def instance_fixture():
    """
    This method calls the class being tested.
    :return: The class with mock arguments.
    """
    mock_url = "mock_url"
    mock_token = "mock_token"
    return CsvToNetbox(mock_url, mock_token)


def test_check_file_path_valid(instance):
    """
    This test checks that the method doesn't raise any errors for valid filepaths.
    """
    mock_file_path = "."
    instance.check_file_path(mock_file_path)

    # with not raises(FileNotFoundError):
    #     instance.read_csv(mock_file_path)


def test_check_file_path_invalid(instance):
    """
    This test checks that the method raises an error when the filepath is invalid.
    """
    mock_file_path = ">"
    with raises(FileNotFoundError):
        instance.check_file_path(mock_file_path)
