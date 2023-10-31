"""
Tests for Sanctions API v1 views.
"""
import json
from unittest import mock

from rest_framework.reverse import reverse

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
        }
        self.token = self.generate_jwt_token_header(self.user)

    def test_sdn_check_missing_args(self):
        response = self.client.post(self.url, HTTP_AUTHORIZATION=self.token)
        assert response.status_code == 400

    # TODO: add test for test_sdn_check_search_fails_uses_fallback

    @mock.patch('sanctions.apps.api_client.sdn_client.SDNClient.search')
    def test_sdn_check_search_succeeds(
        self,
        mock_search
    ):
        mock_search.return_value = {'total': 4}
        self.set_jwt_cookie(self.user.id)
        response = self.client.post(
            self.url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token,
            data=json.dumps(self.post_data)
        )
        assert response.status_code == 200
        assert response.json()['hit_count'] == 4
        assert response.json()['sdn_response'] == {'total': 4}
        # TODO: add mock_fallback.assert_not_called()
