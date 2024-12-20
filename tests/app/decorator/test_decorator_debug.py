"""TcEx Framework Module"""

# standard library
from collections.abc import Callable

# third-party
import pytest

# first-party
from tcex.app.decorator.debug import Debug
from tests.mock_app import MockApp


class TestIterateOnArgDecorators:
    """Test the TcEx Decorators."""

    args = None
    tcex = None

    @Debug()  # type: ignore
    def debug(self, color, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return color, kwargs.get('colors')

    @pytest.mark.parametrize(
        'arg,value',
        [('one', b'1'), ('two', [b'2']), ('three', '3'), ('four', ['4'])],
    )
    def test_debug(self, arg, value, playbook_app: Callable[..., MockApp]):
        """Test ReadArg decorator."""
        self.tcex = playbook_app().tcex

        # call decorated method and get result
        result = self.debug(arg, colors=value)
        assert result == (arg, value)
