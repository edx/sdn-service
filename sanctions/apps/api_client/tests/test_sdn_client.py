"""
Tests for SDN API client.
"""
import json
from urllib.parse import urlencode

import mock
import responses
from django.test import TestCase
from requests.exceptions import HTTPError, Timeout

from sanctions.apps.api_client.sdn_client import SDNClient


class TestSDNClient(TestCase):
    """
    Test SDN API client.
    """

    def setUp(self):
        super(TestSDNClient, self).setUp()
        self.name = 'Dr. Evil'
        self.city = 'Top-secret liar'
        self.country = 'EL'
        self.lms_user_id = 123
        self.sdn_api_url = 'http://sdn-test.fake/'
        self.sdn_api_key = 'fake-key'
        self.sdn_api_list = 'SDN, ISN'

        self.sdn_api_client = SDNClient(
            self.sdn_api_url,
            self.sdn_api_key,
            self.sdn_api_list,
        )

    def mock_sdn_api_response(self, response, status_code=200):
        """ Mock the US Treasury SDN API response. """
        params_dict = {
            'sources': self.sdn_api_list,
            'type': 'individual',
            'name': str(self.name).encode('utf-8'),
            'city': str(self.city).encode('utf-8'),
            'countries': self.country
        }

        params = urlencode(params_dict)
        sdn_check_url = '{api_url}?{params}'.format(
            api_url=self.sdn_api_url,
            params=params
        )
        auth_header = {'subscription-key': '{}'.format(self.sdn_api_key)}

        responses.add(
            responses.GET,
            sdn_check_url,
            headers=auth_header,
            status=status_code,
            body=response() if callable(response) else response,
            content_type='application/json'
        )

    @responses.activate
    def test_sdn_search_timeout(self):
        """
        Verify SDNClient search logs an exception if the request times out.
        """
        self.mock_sdn_api_response(Timeout)
        with self.assertRaises(Timeout):
            with mock.patch('sanctions.apps.api_client.sdn_client.logger.exception') as mock_logger:
                self.sdn_api_client.search(self.lms_user_id, self.name, self.city, self.country)
                assert mock_logger.is_called()

    @responses.activate
    def test_sdn_search_failure(self):
        """
        Verify SDNClient search logs an exception if SDN API call fails.
        """
        self.mock_sdn_api_response(HTTPError, status_code=400)
        with self.assertRaises(HTTPError):
            with mock.patch('sanctions.apps.api_client.sdn_client.logger.exception') as mock_logger:
                response = self.sdn_api_client.search(self.lms_user_id, self.name, self.city, self.country)
                assert mock_logger.is_called()
                assert response.status_code == 400

    @responses.activate
    def test_sdn_search_success(self):
        """
        Verify SDNClient search returns the number of matches.
        """
        sdn_response = {'total': 1}
        self.mock_sdn_api_response(json.dumps(sdn_response), status_code=200)
        response = self.sdn_api_client.search(self.lms_user_id, self.name, self.city, self.country)
        assert response == sdn_response
