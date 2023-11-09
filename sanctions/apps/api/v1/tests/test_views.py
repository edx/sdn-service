"""
Tests for Sanctions API v1 views.
"""
import json
from unittest import mock

from django.db.utils import OperationalError
from requests.exceptions import HTTPError
from rest_framework.reverse import reverse

from sanctions.apps.sanctions.models import SanctionsCheckFailure
from test_utils import APITest


class TestSDNCheckView(APITest):
    """ Test SDNCheckView. """

    def setUp(self):
        super().setUp()
        self.url = reverse('api:v1:sdn-check')
        self.post_data = {
            'lms_user_id': self.user.lms_user_id,
            'full_name': 'Din Grogu',
            'city': 'Jedi Temple',
            'country': 'SW',
            'system_identifier': 'a new django IDA'
        }
        self.user.is_staff = True
        self.user.save()

    def test_sdn_check_missing_args_returns_400(self):
        self.set_jwt_cookie(self.user.id)
        response = self.client.post(self.url)
        assert response.status_code == 400

    @mock.patch('sanctions.apps.api.v1.views.checkSDNFallback')
    @mock.patch('sanctions.apps.api_client.sdn_client.SDNClient.search')
    def test_sdn_check_search_fails_uses_fallback(self, mock_search, mock_fallback):
        mock_search.side_effect = [HTTPError]
        mock_fallback.return_value = 0
        self.set_jwt_cookie(self.user.id)
        response = self.client.post(
            self.url,
            content_type='application/json',
            data=json.dumps(self.post_data)
        )
        assert response.status_code == 200
        assert response.json()['hit_count'] == 0
        assert mock_fallback.is_called()
    def test_sdn_check_no_jwt_returns_401(self):
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_sdn_check_non_staff_returns_403(self):
        self.user.is_staff = False
        self.user.save()

        self.set_jwt_cookie(self.user.id)
        response = self.client.post(self.url)
        assert response.status_code == 403

    # TODO: add test for test_sdn_check_search_fails_uses_fallback

    @mock.patch('sanctions.apps.api.v1.views.checkSDNFallback')
    @mock.patch('sanctions.apps.api_client.sdn_client.SDNClient.search')
    def test_sdn_check_search_succeeds(
        self,
        mock_search,
        mock_fallback
    ):
        mock_search.return_value = {'total': 4}
        self.set_jwt_cookie(self.user.id)
        response = self.client.post(
            self.url,
            content_type='application/json',
            data=json.dumps(self.post_data)
        )
        assert response.status_code == 200
        assert response.json()['hit_count'] == 4
        assert response.json()['sdn_response'] == {'total': 4}
        mock_fallback.assert_not_called()

        assert SanctionsCheckFailure.objects.count() == 1
        failure_record = SanctionsCheckFailure.objects.first()
        assert failure_record.full_name == 'Din Grogu'
        assert failure_record.username is None
        assert failure_record.lms_user_id == self.user.lms_user_id
        assert failure_record.city == 'Jedi Temple'
        assert failure_record.country == 'SW'
        assert failure_record.sanctions_type == 'ISN,SDN'
        assert failure_record.system_identifier == 'a new django IDA'
        assert failure_record.metadata == {}
        assert failure_record.sanctions_response == {'total': 4}

    @mock.patch('sanctions.apps.api.v1.views.SanctionsCheckFailure.objects.create')
    @mock.patch('sanctions.apps.api_client.sdn_client.SDNClient.search')
    def test_sdn_check_search_succeeds_despite_DB_issue(
        self,
        mock_search,
        mock_sanction_record_create,
    ):
        """
        In the case that we are unable to create a DB object, we should log
        and error and return the results from the SDN API to the caller.
        """
        mock_search.return_value = {'total': 4}
        self.set_jwt_cookie(self.user.id)
        mock_sanction_record_create.side_effect = OperationalError('Connection timed out')

        response = self.client.post(
            self.url,
            content_type='application/json',
            data=json.dumps(self.post_data)
        )

        assert response.status_code == 200
        assert response.json()['hit_count'] == 4
        assert response.json()['sdn_response'] == {'total': 4}

        assert SanctionsCheckFailure.objects.count() == 0
