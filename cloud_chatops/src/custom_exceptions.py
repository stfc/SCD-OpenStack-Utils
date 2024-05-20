class RepoNotFound(Exception):
    """
    Error: The requested repository does not exist on GitHub.
    Check for a typo in the repository name.
    Check that the repository is owned by stfc.
    """

    pass


class UnknownHTTPError(Exception):
    """Error: The received HTTP response is unexpected."""

    pass


class RepositoriesNotGiven(Exception):
    """Error: repos.csv does not contain any repositories."""

    pass


class TokensNotGiven(Exception):
    """Error: Token values are either empty or not given."""

    pass


class UserMapNotGiven(Exception):
    """Error: User map is empty."""

    pass

class BadGitHubToken(Exception):
    """Error: GitHub REST Api token is invalid."""
