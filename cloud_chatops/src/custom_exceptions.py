"""This module contains custom exceptions to handle errors for the Application."""


class RepoNotFound(Exception):
    """Error: The requested repository does not exist on GitHub."""


class UnknownHTTPError(Exception):
    """Error: The received HTTP response is unexpected."""


class RepositoriesNotGiven(Exception):
    """Error: repos.csv does not contain any repositories."""


class TokensNotGiven(Exception):
    """Error: Token values are either empty or not given."""


class UserMapNotGiven(Exception):
    """Error: User map is empty."""


class BadGitHubToken(Exception):
    """Error: GitHub REST Api token is invalid."""
