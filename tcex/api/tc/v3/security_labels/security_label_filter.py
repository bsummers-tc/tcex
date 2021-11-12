"""Security_Label TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class SecurityLabelFilter(FilterABC):
    """Filter Object for SecurityLabels"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.SECURITY_LABELS.value

    def color(self, operator: Enum, color: str) -> None:
        """Filter Color based on **color** keyword.

        Args:
            operator: The operator enum for the filter.
            color: The color of the security label (in hex triplet format).
        """
        self._tql.add_filter('color', operator, color, TqlType.STRING)

    def date_added(self, operator: Enum, date_added: str) -> None:
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the security label was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def description(self, operator: Enum, description: str) -> None:
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the security label.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    @property
    def has_group(self):
        """Return **GroupFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.groups.group_filter import GroupFilter

        groups = GroupFilter(Tql())
        self._tql.add_filter('hasGroup', TqlOperator.EQ, groups, TqlType.SUB_QUERY)
        return groups

    def has_group_attribute(self, operator: Enum, has_group_attribute: int) -> None:
        """Filter Associated Group based on **hasGroupAttribute** keyword.

        Args:
            operator: The operator enum for the filter.
            has_group_attribute: A nested query for association to other groups.
        """
        self._tql.add_filter('hasGroupAttribute', operator, has_group_attribute, TqlType.INTEGER)

    @property
    def has_indicator(self):
        """Return **IndicatorFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter

        indicators = IndicatorFilter(Tql())
        self._tql.add_filter('hasIndicator', TqlOperator.EQ, indicators, TqlType.SUB_QUERY)
        return indicators

    def has_indicator_attribute(self, operator: Enum, has_indicator_attribute: int) -> None:
        """Filter Associated Indicator based on **hasIndicatorAttribute** keyword.

        Args:
            operator: The operator enum for the filter.
            has_indicator_attribute: A nested query for association to other indicators.
        """
        self._tql.add_filter(
            'hasIndicatorAttribute', operator, has_indicator_attribute, TqlType.INTEGER
        )

    def has_victim(self, operator: Enum, has_victim: int) -> None:
        """Filter Associated Victim based on **hasVictim** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victim: A nested query for association to other victims.
        """
        self._tql.add_filter('hasVictim', operator, has_victim, TqlType.INTEGER)

    def has_victim_attribute(self, operator: Enum, has_victim_attribute: int) -> None:
        """Filter Associated Victim based on **hasVictimAttribute** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victim_attribute: A nested query for association to other victims.
        """
        self._tql.add_filter('hasVictimAttribute', operator, has_victim_attribute, TqlType.INTEGER)

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the security label.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the security label.
        """
        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def owner(self, operator: Enum, owner: int) -> None:
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the security label.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the security label.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The name of the security label.
        """
        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def victim_id(self, operator: Enum, victim_id: int) -> None:
        """Filter Victim ID based on **victimId** keyword.

        Args:
            operator: The operator enum for the filter.
            victim_id: The ID of the victim the security label is applied to.
        """
        self._tql.add_filter('victimId', operator, victim_id, TqlType.INTEGER)