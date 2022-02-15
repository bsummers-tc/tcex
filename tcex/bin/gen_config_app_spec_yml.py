"""TcEx Generate Configurations CLI Command"""
# standard library
import json

# first-party
from tcex.app_config import AppSpecYml, InstallJson, JobJson, LayoutJson
from tcex.app_config.models import AppSpecYmlModel
from tcex.bin.bin_abc import BinABC


class GenConfigAppSpecYml(BinABC):
    """Generate App Config File"""

    def __init__(self) -> None:
        """Initialize class properties."""
        super().__init__()

        # properties
        self.filename = 'app_spec.yml'
        self.asy = AppSpecYml(logger=self.log)
        self.ij = InstallJson(logger=self.log)
        self.jj = JobJson(logger=self.log)
        self.lj = LayoutJson(logger=self.log)

    def _add_standard_fields(self, app_spec_yml_data: dict) -> None:
        """Add field that apply to ALL App types."""
        app_spec_yml_data.update(
            {
                'allowOnDemand': self.ij.model.allow_on_demand,
                'apiUserTokenParam': self.ij.model.api_user_token_param,
                'appId': str(self.ij.model.app_id),
                'deprecatesApps': self.ij.model.deprecates_apps,
                'displayName': self.ij.model.display_name,
                'features': self.ij.model.features,
                'labels': self.ij.model.labels,
                'languageVersion': self.ij.model.language_version,
                'listDelimiter': self.ij.model.list_delimiter,
                'minServerVersion': str(self.ij.model.min_server_version),
                'note': self.ij.model.note,
                'programLanguage': self.ij.model.program_language,
                'programMain': self.ij.model.program_main,
                'programVersion': str(self.ij.model.program_version),
                'runtimeLevel': self.ij.model.runtime_level,
            }
        )

    def _add_category(self, app_spec_yml_data: dict) -> None:
        """Add category."""
        _category = ''
        if self.ij.model.runtime_level.lower() != 'organization':
            _category = self.ij.model.playbook.type or ''
        app_spec_yml_data['category'] = _category

    def _add_note_per_action(self, app_spec_yml_data: dict) -> None:
        """Add note per action."""
        _notes_per_action = []
        param = self.ij.model.get_param('tc_action')
        if param.valid_values:
            for action in param.valid_values:
                _notes_per_action.append({'action': action, 'note': ''})

            app_spec_yml_data['notesPerAction'] = _notes_per_action

    def _add_organization(self, app_spec_yml_data: dict) -> None:
        """Add asy.organization."""
        if self.ij.model.runtime_level.lower() == 'organization':
            app_spec_yml_data.setdefault('organization', {})
            if self.ij.model.publish_out_files:
                app_spec_yml_data['organization'][
                    'publishOutFiles'
                ] = self.ij.model.publish_out_files
            if self.ij.model.repeating_minutes:
                app_spec_yml_data['organization'][
                    'repeatingMinutes'
                ] = self.ij.model.repeating_minutes

    def _add_output_data(self, app_spec_yml_data: dict) -> None:
        """Add asy.outputData."""
        if self.ij.model.runtime_level.lower() != 'organization':
            # build outputs based on display value
            _output_data_temp = {}
            for o in self.lj.model.outputs:
                _output_data_temp.setdefault(o.display, []).append(o.name)

            _output_data = []
            for display, names in _output_data_temp.items():
                _output_variables = []
                for name in names:
                    _output_variables.append(self.ij.model.get_output(name).dict(by_alias=True))

                _output_data.append({'display': display, 'outputVariables': _output_variables})

            app_spec_yml_data['outputData'] = _output_data

            # if not in layout.json and not hidden, add to output data

    def _add_playbook(self, app_spec_yml_data: dict) -> None:
        """Add asy.playbook."""
        if self.ij.model.runtime_level.lower() != 'organization':
            app_spec_yml_data.setdefault('playbook', {})
            if self.ij.model.playbook.retry:
                app_spec_yml_data['playbook']['retry'] = self.ij.model.playbook.retry

    @staticmethod
    def _add_release_notes(app_spec_yml_data: dict) -> None:
        """Add release_notes."""
        app_spec_yml_data['releaseNotes'] = [
            {
                'notes': ['Initial Release'],
                'version': '1.0.0',
            }
        ]

    def _add_sections(self, app_spec_yml_data: dict) -> None:
        """Return params from ij and lj formatted for app_spec."""
        if self.lj.has_layout:
            # handle layout based Apps
            _current_data = [i.dict(by_alias=True) for i in self.lj.model.inputs]
        else:
            # handle non-layout based Apps
            _current_data = [
                {
                    'parameters': [p.dict(by_alias=True) for p in self.ij.model.params],
                    'title': 'Inputs',
                }
            ]

        sections = []
        for section in _current_data:
            _section_data = {'sectionName': section.get('title'), 'params': []}
            for p in section.get('parameters', []):
                param = self.ij.model.get_param(p.get('name')).dict(by_alias=True)
                param['display'] = p.get('display')
                _section_data['params'].append(param)
            sections.append(_section_data)

        app_spec_yml_data['sections'] = sections

    def generate(self) -> None:
        """Generate the layout.json file data."""
        app_spec_yml_data = {}

        # add release notes
        self._add_release_notes(app_spec_yml_data)

        # add standard fields
        self._add_standard_fields(app_spec_yml_data)

        # add category
        self._add_category(app_spec_yml_data)

        # add note per action
        self._add_note_per_action(app_spec_yml_data)

        # add organization (feed, jobs, etc)
        self._add_organization(app_spec_yml_data)

        # add playbook (retry)
        self._add_playbook(app_spec_yml_data)

        # add sections
        self._add_sections(app_spec_yml_data)

        # add output data
        self._add_output_data(app_spec_yml_data)

        # parse and validate the data (use json so that json_encoder convert complex types)
        asy_data = json.loads(
            AppSpecYmlModel(**app_spec_yml_data).json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
                sort_keys=False,
            )
        )

        # force order of keys
        return self.asy.dict_to_yaml(self.asy.order_data(asy_data))

        # return self.asy.dict_to_yaml(
        #     json.loads(
        #         AppSpecYmlModel(**app_spec_yml_data).json(
        #             by_alias=True, exclude_defaults=True, exclude_none=True, exclude_unset=True
        #         )
        #     )
        # )

    @staticmethod
    def generate_schema():
        """Return the schema for the install.json file."""
        return AppSpecYmlModel.schema_json(indent=2, sort_keys=True)