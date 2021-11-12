"""Adversary_Asset / Adversary_Assets Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils

# json-encoder
json_encoders = {datetime: lambda v: v.isoformat()}


class AdversaryAssetsModel(
    BaseModel,
    title='AdversaryAssets Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Adversary_Assets Model"""

    data: Optional[List['AdversaryAssetModel']] = Field(
        [],
        description='The data for the AdversaryAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AdversaryAssetDataModel(
    BaseModel,
    title='AdversaryAsset Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Adversary_Assets Data Model"""

    data: Optional[List['AdversaryAssetModel']] = Field(
        [],
        description='The data for the AdversaryAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AdversaryAssetModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='AdversaryAsset Model',
    validate_assignment=True,
    json_encoders=json_encoders,
):
    """Adversary_Asset Model"""

    account_name: Optional[str] = Field(
        None,
        applies_to=['SocialNetwork', 'NetworkAccount'],
        conditional_required=['SocialNetwork', 'NetworkAccount'],
        description='The network name.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='accountName',
    )
    address: Optional[str] = Field(
        None,
        applies_to=['EmailAddress'],
        conditional_required=['EmailAddress'],
        description='The email address associated with the E-Mail Address asset.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='address',
    )
    address_type: Optional[str] = Field(
        None,
        applies_to=['EmailAddress'],
        conditional_required=['EmailAddress'],
        description='The type of the E-Mail Address asset.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='addressType',
    )
    associated_groups: Optional['GroupsModel'] = Field(
        None,
        description='A list of groups that this victim asset is associated with.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    network_type: Optional[str] = Field(
        None,
        applies_to=['NetworkAccount'],
        conditional_required=['NetworkAccount'],
        description='The type of network.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='networkType',
    )
    phone: Optional[str] = Field(
        None,
        applies_to=['Phone'],
        conditional_required=['Phone'],
        description='The phone number of the asset.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='phone',
    )
    social_network: Optional[str] = Field(
        None,
        applies_to=['SocialNetwork'],
        conditional_required=['SocialNetwork'],
        description='The type of social network.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='socialNetwork',
    )
    type: Optional[str] = Field(
        None,
        description='Type of victim asset.',
        methods=['POST'],
        min_length=1,
        read_only=False,
        title='type',
        updatable=False,
    )
    victim_id: Optional[int] = Field(
        None,
        description='Victim id of victim asset.',
        methods=['POST'],
        read_only=False,
        title='victimId',
        updatable=False,
    )
    website: Optional[str] = Field(
        None,
        applies_to=['WebSite'],
        conditional_required=['WebSite'],
        description='The website of the asset.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='website',
    )

    @validator('associated_groups', always=True)
    def _validate_associated_groups(cls, v):
        if not v:
            return GroupsModel()
        return v


# first-party
from tcex.api.tc.v3.groups.group_model import GroupsModel

# add forward references
AdversaryAssetDataModel.update_forward_refs()
AdversaryAssetModel.update_forward_refs()
AdversaryAssetsModel.update_forward_refs()