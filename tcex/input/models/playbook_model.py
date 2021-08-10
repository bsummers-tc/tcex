"""Playbook Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Field


class PlaybookModel(BaseModel):
    """Playbook Model

    Supported for the following runtimeLevel:
    * Playbook
    """

    tc_playbook_kvstore_context: str = Field(
        None,
        alias='tc_playbook_db_context',
        description='The KV Store context for the current App execution.',
        inclusion_reason='runtimeLevel',
    )
    tc_playbook_out_variables: Optional[list] = Field(
        None,
        description='The list of requested output variables.',
        inclusion_reason='runtimeLevel',
    )