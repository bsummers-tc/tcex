"""TcEx Framework Module"""

# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class SubtypeFilter(FilterABC):
    """Filter Object for Subtypes"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.SUBTYPES.value

    def description(self, operator: Enum, description: list | str):
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the subtype.
        """
        if isinstance(description, list) and operator not in self.list_types:
            ex_msg = (
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )
            raise RuntimeError(ex_msg)

        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def id(self, operator: Enum, id: int | list):  # noqa: A002
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the subtype.
        """
        if isinstance(id, list) and operator not in self.list_types:
            ex_msg = (
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )
            raise RuntimeError(ex_msg)

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def name(self, operator: Enum, name: list | str):
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the subtype.
        """
        if isinstance(name, list) and operator not in self.list_types:
            ex_msg = (
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )
            raise RuntimeError(ex_msg)

        self._tql.add_filter('name', operator, name, TqlType.STRING)
