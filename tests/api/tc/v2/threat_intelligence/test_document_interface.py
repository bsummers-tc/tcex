"""TcEx Framework Module"""

# standard library
import os
import time
from random import randint
from typing import cast

# third-party
from _pytest.fixtures import FixtureRequest

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.document import Document
from tcex.tcex import TcEx
from tests.api.tc.v2.threat_intelligence.ti_helper import TestThreatIntelligence, TIHelper


class TestDocumentGroups(TestThreatIntelligence):
    """Test TcEx Document Groups."""

    group_type = 'Document'
    owner = os.getenv('TC_OWNER')
    required_fields = {'file_name': 'pytest.pdf'}
    tcex: TcEx

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.group_type, required_fields=self.required_fields)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def tests_ti_document_create(self):
        """Create a group using specific interface."""
        group_data = {
            'fileName': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.document(**group_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve group for asserts
        group_data['unique_id'] = ti.unique_id
        ti = self.ti.document(**group_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get(ti.api_entity) == group_data.get(ti.api_entity)

        # cleanup group
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_document_add_attribute(self, request: FixtureRequest):
        """Test group add attribute."""
        super().group_add_attribute(request)

    def tests_ti_document_add_label(self):
        """Test group add label."""
        super().group_add_label()

    def tests_ti_document_add_tag(self, request: FixtureRequest):
        """Test group add tag."""
        super().group_add_tag(request)

    def tests_ti_document_delete(self):
        """Test group delete."""
        super().group_delete()

    def tests_ti_document_get(self):
        """Test group get with generic group method."""
        super().group_get()

    def tests_ti_document_get_filter(self):
        """Test group get with filter."""
        super().group_get_filter()

    def tests_ti_document_get_includes(self, request: FixtureRequest):
        """Test group get with includes."""
        super().group_get_includes(request)

    def tests_ti_document_get_attribute(self, request: FixtureRequest):
        """Test group get attribute."""
        super().group_get_attribute(request)

    def tests_ti_document_get_label(self):
        """Test group get label."""
        super().group_get_label()

    def tests_ti_document_get_tag(self, request: FixtureRequest):
        """Test group get tag."""
        super().group_get_tag(request)

    def tests_ti_document_update(self, request: FixtureRequest):
        """Test updating group metadata."""
        super().group_update(request)

    #
    # Custom test cases
    #

    def tests_ti_document_download(self):
        """Create a group using specific interface."""
        helper_ti = cast(Document, self.ti_helper.create_group())

        # update file content
        file_content = b'pytest content'
        r = helper_ti.file_content(file_content)
        assert r.status_code == 200

        # add a small delay to allow file to be processed
        time.sleep(2)

        # download file
        r = helper_ti.download()
        assert r.status_code == 200
        assert r.text == file_content.decode('utf-8')

    def tests_ti_document_download_no_update(self):
        """Create a group using specific interface."""
        group_data = {
            'file_name': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.document(**group_data)

        try:
            ti.download()
            assert False, 'failed to catch group method call with no id.'
        except RuntimeError:
            assert True, 'caught group method call with no id'

    def tests_ti_document_file_content(self):
        """Update file content value."""
        helper_ti = cast(Document, self.ti_helper.create_group())

        # update file content
        file_content = b'pytest content'
        r = helper_ti.file_content(file_content)
        assert r.status_code == 200

    def tests_ti_document_file_content_no_update(self):
        """Create a group using specific interface."""
        group_data = {
            'file_name': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.document(**group_data)

        try:
            ti.file_content(b'pytest content')
            assert False, 'failed to catch group method call with no id.'
        except RuntimeError:
            assert True, 'caught group method call with no id'

    def tests_ti_document_file_name(self, request: FixtureRequest):
        """Update file name value."""
        helper_ti = cast(Document, self.ti_helper.create_group())

        # update file name
        file_name = request.node.name
        r = helper_ti.file_name(file_name)
        assert r.status_code == 200

    def tests_ti_document_file_name_no_update(self, request: FixtureRequest):
        """Create a group using specific interface."""
        group_data = {
            'file_name': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.document(**group_data)

        try:
            ti.file_name(request.node.name)
            assert False, 'failed to catch group method call with no id.'
        except RuntimeError:
            assert True, 'caught group method call with no id'

    def tests_ti_document_file_size(self):
        """Update file size value."""
        helper_ti = cast(Document, self.ti_helper.create_group())

        # update file size
        file_size = str(randint(10, 20))
        r = helper_ti.file_size(file_size)
        assert r.status_code == 200

    def tests_ti_document_file_size_no_update(self):
        """Create a group using specific interface."""
        group_data = {
            'file_name': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.document(**group_data)

        try:
            ti.file_size(10)
            assert False, 'failed to catch group method call with no id.'
        except RuntimeError:
            assert True, 'caught group method call with no id'

    def tests_ti_document_malware(self, request: FixtureRequest):
        """Update file size value."""
        helper_ti = cast(Document, self.ti_helper.create_group())

        file_data = {
            'file_name': request.node.name,
            'malware': True,
            'password': 'TCInfected',
        }
        r = helper_ti.malware(**file_data)
        assert r.status_code == 200

    def tests_ti_document_malware_no_update(self, request: FixtureRequest):
        """Create a group using specific interface."""
        group_data = {
            'file_name': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.document(**group_data)

        try:
            file_data = {
                'file_name': request.node.name,
                'malware': True,
                'password': 'TCInfected',
            }
            ti.malware(**file_data)
            assert False, 'failed to catch group method call with no id.'
        except RuntimeError:
            assert True, 'caught group method call with no id'
