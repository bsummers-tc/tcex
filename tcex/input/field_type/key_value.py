"""TcEx Framework Module"""

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_core.core_schema import ValidationInfo

from tcex.input.field_type.binary import Binary
from tcex.input.field_type.exception import InvalidEmptyValue
from tcex.input.field_type.sensitive import Sensitive
from tcex.input.field_type.string import String
from tcex.input.field_type.tc_entity import TCEntity


class KeyValue(BaseModel):
    """Model for KeyValue Input."""

    key: str
    type: str | None = None
    # KeyValue is self-referential; quote the whole union (not just the self-reference) so the
    # recursive forward ref is a single string annotation, resolved by model_rebuild() below.
    value: 'list[KeyValue] | KeyValue | list[TCEntity] | TCEntity | list[String] | String | list[Binary] | Binary | Sensitive'  # noqa: E501

    @field_validator('key')
    @classmethod
    def non_empty_string(cls, value: str, info: ValidationInfo) -> str:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=info.field_name or 'Unknown')
        return value

    model_config = ConfigDict(validate_assignment=True)


KeyValue.model_rebuild()


def key_value(allow_none=False):
    """Return configured instance of KeyValue model."""
    key_value_model = KeyValue
    if allow_none is True:

        class _KeyValue(KeyValue):
            value: (
                list[KeyValue]
                | KeyValue
                | list[TCEntity]
                | TCEntity
                | list[String]
                | String
                | list[Binary]
                | Binary
                | Sensitive
                | None
            ) = None

        key_value_model = _KeyValue
    return key_value_model
