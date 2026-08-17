import ast
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

ROOT_TEST_DATA_FP = Path(__file__).parent / "test_data"

# Must match the epoch in every expected.txt (1786453260).
END_TIME = datetime(2026, 8, 11, 12, 0, 0, tzinfo=timezone.utc)
START_TIME = datetime(2026, 8, 11, 11, 0, 0, tzinfo=timezone.utc)
INSTANCE = "PreProd"


def load_example_data(path: Path) -> list[dict[str, Any]]:
    """
    load file containing example data - mock results from source
    :param path: Path to example data
    :returns: A list of dict to mock output of source
    """
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            # try to read in line as a python dictionary
            row = ast.literal_eval(line)
        except (ValueError, SyntaxError) as exc:
            raise ValueError(f"{path}:{i}: not a Python literal: {line!r}") from exc
        if not isinstance(row, dict):
            raise TypeError(f"{path}:{i}: expected dict, got {type(row).__name__}")
        rows.append(row)
    return rows


def load_expected_data(path: Path) -> str:
    """
    Read expected sink payload from filepath
    :param path: Path to example data
    :returns: A string that will be passed to source
    """
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return "\n".join(lines)



@pytest.fixture
def mock_source():
    source = MagicMock()
    return source


@pytest.fixture
def mock_sink():
    sink = MagicMock()
    sink.instance = INSTANCE
    return sink