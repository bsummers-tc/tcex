"""TcEx Framework Playbook module"""
# standard library
import re
from typing import Any, List, Optional, Union

# first-party
from tcex.key_value_store import KeyValueApi, KeyValueRedis

from .playbook_abc import PlaybookABC


class Playbook(PlaybookABC):
    """Playbook methods for accessing key value store.

    Args:
        key_value_store: A KV store instance.
        context: The KV Store context/session_id. For PB Apps the context is provided on
            startup, but for service Apps each request gets a different context.
        output_variables: The requested output variables. For PB Apps outputs are provided on
            startup, but for service Apps each request gets different outputs.
    """

    def __init__(
        self,
        key_value_store: Union[KeyValueApi, KeyValueRedis],
        context: Optional[str] = None,
        output_variables: Optional[list] = None,
    ) -> None:
        """Initialize the class properties."""
        super().__init__(key_value_store, context, output_variables)

        # properties
        self.output_data = {}

    def add_output(
        self, key: str, value: Any, variable_type: str, append_array: Optional[bool] = True
    ) -> None:
        """Dynamically add output to output_data dictionary to be written to DB later.

        This method provides an alternative and more dynamic way to create output variables in an
        App. Instead of storing the output data manually and writing all at once the data can be
        stored inline, when it is generated and then written before the App completes.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            colors = ['blue', 'red', 'yellow']:
            tcex.playbook.add_output('app.colors', colors, 'StringArray')

            tcex.playbook.write_output()  #  writes the output stored in output_data

        .. code-block:: json
            :linenos:
            :lineno-start: 1

            {
                "my_color-String": {
                    "key": "my_color",
                    "type": "String",
                    "value": "blue"
                },
                "my_numbers-String": {
                    "key": "my_numbers",
                    "type": "String",
                    "value": "seven"
                },
                "my_numbers-StringArray": {
                    "key": "my_numbers",
                    "type": "StringArray",
                    "value": ["seven", "five"]
                }
            }

        Args:
            key: The variable name to write to storage.
            value: The value to write to storage.
            variable_type: The variable type being written.
            append_array: If True arrays will be appended instead of being overwritten.
        """
        index = f'{key}-{variable_type}'
        self.output_data.setdefault(index, {})
        if value is None:
            if variable_type not in self._variable_array_types:
                # never append or store None values if not an array
                return
            if not append_array and variable_type in self._variable_array_types:
                # Only store none for array types when append is True
                return

        if variable_type in self._variable_array_types and append_array:
            self.output_data[index].setdefault('key', key)
            self.output_data[index].setdefault('type', variable_type)
            if isinstance(value, list):
                self.output_data[index].setdefault('value', []).extend(value)
            else:
                self.output_data[index].setdefault('value', []).append(value)
        else:
            self.output_data[index] = {'key': key, 'type': variable_type, 'value': value}

    def check_output_variable(self, variable: str) -> bool:
        """Check to see if output variable was requested by downstream app.

        Using the auto generated dictionary of output variables check to see if provided
        variable was requested by downstream app.

        Args:
            variable: The variable name, not the full variable.

        Returns:
            (bool): True, if match found.
        """
        return variable in self.output_variables_by_name

    def create(self, key: str, value: Any) -> str:
        """Create method of CRUD operation for working with KeyValue DB.

        This method will automatically determine the variable type and
        call the appropriate method to write the data.  If a non standard
        type is provided the data will be written as RAW data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result string of DB write.
        """
        data = None
        if key is not None:
            key = key.strip()
            parsed_key = self.parse_variable(key.strip())
            variable_type = parsed_key['type']

            # log/debug
            self.log.debug(f'create variable {key}')
            if variable_type not in ['Binary', 'BinaryArray']:
                self.log.trace(f'variable value: {value}')

            if variable_type in self._variable_single_types:
                data = self._create(key, value)
            elif variable_type in self._variable_array_types:
                data = self._create_array(key, value)
            else:
                data = self.create_raw(key, value)
        return data

    def create_binary(self, key: str, value: bytes) -> str:
        """Create method of CRUD operation for binary data.

        Args:
            key: The variable to write to the Key Value Store.
            value: The data to write to the Key Value Store.

        Returns:
            (str): Result of Key Value Store write.
        """
        supported_variable_type = 'Binary'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_binary_array(self, key: str, value: List[bytes]) -> str:
        """Create method of CRUD operation for binary array data.

        Args:
            key: The variable to write to the Key Value Store.
            value: The data to write to the Key Value Store.

        Returns:
            (str): Result of Key Value Store write.
        """
        supported_variable_type = 'BinaryArray'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_key_value(self, key: str, value: Any) -> str:
        """Create method of CRUD operation for key/value data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write
        """
        supported_variable_type = 'KeyValue'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_key_value_array(self, key: str, value: List[Any]) -> str:
        """Create method of CRUD operation for key/value array data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'KeyValueArray'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_string(self, key: str, value: str) -> str:
        """Create method of CRUD operation for string data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'String'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_string_array(self, key: str, value: List[str]) -> str:
        """Create method of CRUD operation for string array data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'StringArray'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_tc_entity(self, key: str, value: dict) -> str:
        """Create method of CRUD operation for TC entity data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'TCEntity'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_tc_entity_array(self, key: str, value: List[dict]) -> str:
        """Create method of CRUD operation for TC entity array data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = ['TCEntityArray', 'TCEnhancedEntity', 'TCEnhancedEntityArray']
        if self.variable_type(key) not in supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_output(self, key: str, value: Any, variable_type: Optional[str] = None) -> str:
        """Alias for Create method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if provided variable was requested by
        a downstream app and if so create the data in the KeyValue DB.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.
            variable_type: The variable type being written.

        Returns:
            (str): Result string of DB write.
        """
        #  This is if no downstream variables are requested then nothing should be returned.
        if not self.output_variables_by_type:  # pragma: no cover
            self.log.debug(f'Variable {key} was NOT requested by downstream app.')
            return None

        if key is None:
            self.log.info('Key has a none value and will not be written.')
            return None

        if value is None:
            self.log.info(f'Variable {key} has a none value and will not be written.')
            return None

        key = key.strip()
        key_type = f'{key}-{variable_type}'
        results = None
        if self.output_variables_by_type.get(key_type) is not None:
            # variable key-type has been requested
            v = self.output_variables_by_type.get(key_type)
            self.log.info(f"Variable {v.get('variable')} was requested by downstream App.")
            results = self.create(v.get('variable'), value)
        elif self.output_variables_by_name.get(key) is not None and variable_type is None:
            # variable key has been requested
            v = self.output_variables_by_name.get(key)
            self.log.info(f"Variable {v.get('variable')} was requested by downstream App.")
            results = self.create(v.get('variable'), value)
        else:
            self.log.trace(f'requested output variables: {self.output_variables_by_name}')
            self.log.debug(f'Variable {key} was NOT requested by downstream app.')

        return results

    def delete(self, key: str) -> str:
        """Delete method of CRUD operation for all data types.

        This method is only supported when using key_value_redis.

        Args:
            key: The variable to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        data = None
        if key is not None:
            data = self.key_value_store.delete(self._context, key.strip())
        else:  # pragma: no cover
            self.log.warning('The key field was None.')
        return data

    def is_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted variable."""
        if not isinstance(key, str):
            return False
        if re.match(self._variable_match, key):
            return True
        return False

    @property
    def output_variables_by_name(self) -> dict:
        """Return output variables stored as name dict."""
        if self._output_variables_by_name is None:
            self._parse_output_variables()
        return self._output_variables_by_name

    @property
    def output_variables_by_type(self) -> dict:
        """Return output variables stored as name-type dict."""
        if self._output_variables_by_type is None:
            self._parse_output_variables()
        return self._output_variables_by_type

    def parse_variable(self, variable: str) -> dict:
        """Parse an input or output variable.

        **Example Variable**::

        #App:1234:output!String

        Args:
            variable: The variable name to parse.

        Returns:
            (dict): Result of parsed string.
        """
        data = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self._variable_match, variable):
                var = re.search(self._variable_parse, variable)
                data = {
                    'root': var.group(0),
                    'job_id': var.group(2),
                    'name': var.group(3),
                    'type': var.group(4),
                }
        return data

    def read(self, key: str, array: Optional[bool] = False, embedded: Optional[bool] = True) -> Any:
        """Read method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if a single variable is passed
        or if "mixed" data is passed and return the results from the DB. It will also
        automatically determine the variable type to read.

        Args:
            key: The variable to read from the DB.
            array: Convert string/dict to Array/List before returning.
            embedded: Resolve embedded variables.

        Returns:
            (any): Results retrieved from DB
        """
        # if a non-variable value is passed it should be the default
        value = key
        if isinstance(key, str):
            key = key.strip()
            variable_type = self.variable_type(key)
            if re.match(self._variable_match, key):
                # only log key if it's a variable
                self.log.debug(f'read variable {key}')
                if variable_type in self._variable_single_types:
                    value = self._read(key=key, embedded=embedded)
                elif variable_type in self._variable_array_types:
                    value = self._read_array(key=key, embedded=embedded)
                else:
                    value = self.read_raw(key)
            else:
                if variable_type == 'String':
                    # replace "\s" with a space only for user input.
                    # using '\\s' will prevent replacement.
                    value = re.sub(r'(?<!\\)\\s', ' ', value)
                    value = re.sub(r'\\\\s', r'\\s', value)

                if embedded:
                    # check for any embedded variables
                    value = self._read_embedded(value)

        # return data as a list
        if array and not isinstance(value, list):
            if value is not None:
                value = [value]
            else:
                # Adding none value to list breaks App logic. It's better to not request
                # Array and build array externally if None values are required.
                value = []

        return value

    def _entity_field(
        self, key: str, field: str, entity_type: Optional[Any] = None, default: Optional[Any] = None
    ) -> list:
        """Read the value of the given key and return the data at the given field of the value.

        This method is used by functions designed to make it easier to get
        data from a particular field from TC(Enhanced)Entity(Array).

        Args:
            key: The variable to read from the DB.
            field: The field to find in the data.
            entity_type: The type of data being collected (valid values: ['groups', 'indicators']).
            default: The value to use for malformed TCEntities or TCEnhancedEntities.

        Returns:
            (list): A list of strings containing the desired values.
        """
        read_results = self.read(key, array=True)
        if not read_results:
            return []

        variable_type = self.variable_type(key).lower()
        enhanced_entity_field = None
        VALID_ENTITY_TYPES = ['group', 'indicator']

        # handle the odd format of tcEnhancedEntityArrays which follow the format detailed here:
        # https://docs.threatconnect.com/en/latest/rest_api/indicators/indicators.html#batch-indicator-input-file-format-v2
        if read_results and variable_type == 'tcenhancedentityarray':
            # type specific values
            if entity_type == 'indicator' and field == 'value':
                enhanced_entity_field = 'summary'
            elif entity_type == 'group' and field == 'value':
                enhanced_entity_field = 'name'
            elif entity_type not in VALID_ENTITY_TYPES:  # pragma: no cover
                message = (
                    f'Invalid entity_type ({entity_type}). Valid options: {VALID_ENTITY_TYPES}.'
                )
                raise RuntimeError(message)

            read_results = read_results[0].get(entity_type, [])

        is_tc_enhanced = enhanced_entity_field and variable_type in [
            'tcenhancedentity',
            'tcenhancedentityarray',
        ]
        is_tc_entity = variable_type in ['tcentity', 'tcentityarray']

        if is_tc_enhanced:
            values = [i.get(enhanced_entity_field, default) for i in read_results]
        elif is_tc_entity:
            values = [i.get(field, default) for i in read_results]
        else:
            values = read_results

        return values

    def read_indicator_values(self, key: str, default: Optional[Any] = None) -> list:
        """Read the value of the given key and return indicators from the value.

        This method will call the `read` method and then will process the data so as to return a
        list of strings where each string is an indicator (the summary of an indicator - e.g.
        ["foo.example.com", "bar.example.com"]).

        Args:
            key: The variable to read from the DB.
            default: The value to use for malformed TCEntities or TCEnhancedEntities.

        Returns:
            (list): A list of strings containing the indicators
        """
        return self._entity_field(key, 'value', entity_type='indicator', default=default)

    def read_group_values(self, key: str, default: Optional[Any] = None) -> list:
        """Read the value of the given key and return group names from the value.

        This method will call the `read` method and then will process the data
        so as to return a list of strings where each string is a group name.

        Args:
            key: The variable to read from the DB.
            default: The value to use for malformed TCEntities or TCEnhancedEntities.

        Returns:
            (list): A list of strings containing the group names
        """
        return self._entity_field(key, 'value', entity_type='group', default=default)

    def read_group_ids(self, key: str, default: Optional[Any] = None) -> list:
        """Read the value of the given key and return group ids from the value.

        This method will call the `read` method and then will process the data
        so as to return a list of strings where each string is a group id.

        Args:
            key: The variable to read from the DB.
            default: The value to use for malformed TCEntities or TCEnhancedEntities.

        Returns:
            (list): A list of strings containing the group ids
        """
        return self._entity_field(key, 'id', entity_type='group', default=default)

    def read_choice(self, key: str, alt_key: str) -> Optional[str]:
        """Read method for choice inputs.

        Behavior:
        * If key is "-- Select --" return None.
        * If key is "-- Variable Input --" return resolved alt_key.
        * Else return resolved value for key.

        Args:
            key: The variable to read from KeyValue Store.
            alt_key: The alternate variable to read from the KeyValue Store.
        """
        if key is None:
            return None

        if key.strip() == '-- Select --':
            return None

        if key.strip() == '-- Variable Input --':
            return self.read(alt_key)

        return self.read(key)

    def read_array(self, key: str, embedded: Optional[bool] = True) -> List[Any]:
        """Read playbook variable and return array for any variable type.

        Args:
            key: The variable to read from the DB.
            embedded: Resolve embedded variables.
        """
        return self.read(key, True, embedded)

    def read_binary(
        self, key: str, b64decode: Optional[bool] = True, decode: Optional[bool] = False
    ) -> Union[bytes, str]:
        """Read method of CRUD operation for binary data.

        Args:
            key: The variable to read from the DB.
            b64decode: If true the data will be base64 decoded.
            decode: If true the data will be decoded to a String.
        """
        return self._read(key, b64decode=b64decode, decode=decode)

    def read_binary_array(
        self, key: str, b64decode: Optional[bool] = True, decode: Optional[bool] = False
    ) -> List[Union[bytes, str]]:
        """Read method of CRUD operation for binary array data.

        Args:
            key: The variable to read from the DB.
            b64decode: If true the data will be base64 decoded.
            decode: If true the data will be decoded to a String.
        """
        return self._read_array(key, b64decode=b64decode, decode=decode)

    def read_key_value(self, key: str, embedded: Optional[bool] = True) -> dict:
        """Read method of CRUD operation for key/value data.

        Args:
            key: The variable to read from the DB.
            embedded: Resolve embedded variables.
        """
        return self._read(key, embedded=embedded)

    def read_key_value_array(self, key: str, embedded: Optional[bool] = True) -> List[dict]:
        """Read method of CRUD operation for key/value array data.

        Args:
            key: The variable to read from the DB.
            embedded: Resolve embedded variables.
        """
        return self._read_array(key, embedded=embedded)

    def read_string(self, key: str, embedded: Optional[bool] = True) -> str:
        """Read method of CRUD operation for string data.

        Args:
            key: The variable to read from the DB.
            embedded: Resolve embedded variables.
        """
        return self._read(key, embedded=embedded)

    def read_string_array(self, key: str, embedded: Optional[bool] = True) -> List[str]:
        """Read method of CRUD operation for string array data.

        Args:
            key: The variable to read from the DB.
            embedded: Resolve embedded variables.
        """
        return self._read_array(key, embedded=embedded)

    def read_tc_entity(self, key: str, embedded: Optional[bool] = True) -> dict:
        """Read method of CRUD operation for TC entity data.

        Args:
            key: The variable to read from the DB.
            embedded: Resolve embedded variables.
        """
        return self._read(key, embedded=embedded)

    def read_tc_entity_array(self, key: str, embedded: Optional[bool] = True) -> List[dict]:
        """Read method of CRUD operation for TC entity array data.

        Args:
            key: The variable to read from the DB.
            embedded: Resolve embedded variables.
        """
        return self._read_array(key, embedded=embedded)

    def variable_type(self, variable: str) -> str:
        """Get the Type from the variable string or default to String type.

        The default type is "String" for those cases when the input variable is
        contains not "DB variable" and is just a String.

        **Example Variable**::

            #App:1234:output!StringArray returns **StringArray**

        **Example String**::

            "My Data" returns **String**

        Args:
            variable: The variable to be parsed
        """
        var_type = 'String'
        if isinstance(variable, str):
            variable = variable.strip()
            if re.match(self._variable_match, variable):
                var_type = re.search(self._variable_parse, variable).group(4)
        return var_type

    def write_output(self):
        """Write all stored output data to storage."""
        for data in self.output_data.values():
            self.create_output(data.get('key'), data.get('value'), data.get('type'))