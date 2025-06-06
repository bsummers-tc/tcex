"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class AttackPattern(Group):
    """Unique API calls for AttackPattern API Endpoints

    Args:
        ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties."""
        super().__init__(
            ti,
            sub_type='Attack Pattern',
            api_entity='attackPattern',
            api_branch='attackPatterns',
            **kwargs,
        )
