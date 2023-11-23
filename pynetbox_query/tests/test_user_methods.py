from unittest.mock import patch

def test_collect_args(mock_vars, mock_parser):
    """
    This test ensures all the correct methods are called.
    """
    with patch(user_method_module_parser) as mock_parser:
        with patch(user_method_module_vars) as mock_vars:
            res = _collect_args()
            mock_parser.assert_called_once()
            mock_parser.return_value.parse_args.assert_called_once()
            mock_vars.assery_called_once_with(mock_parser.return_value.parse_args.return_value)
            assert res == mock_vars.return_value