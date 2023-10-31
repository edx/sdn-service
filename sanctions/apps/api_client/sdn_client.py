"""
API client for calls to trade.gov's SDN API.
"""
import logging
from urllib.parse import urlencode

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SDNClient:
    """API client that handles calls to the US Treasury SDN API."""

    def __init__(self, sdn_api_url, sdn_api_key, sdn_api_list):
        self.sdn_api_url = sdn_api_url
        self.sdn_api_key = sdn_api_key
        self.sdn_api_list = sdn_api_list

    def search(self, lms_user_id, name, city, country):
        """
        Searches the OFAC list for an individual with the specified details.

        The check returns zero hits if:
        * request to the SDN API times out
        * SDN API returns a non-200 status code response
        * user is not found on the SDN list

        Args:
        lms_user_id (int): User's ID in the LMS, for logging purposes.
        name (str): Individual's full name.
        city (str): Individual's city.
        country (str): ISO 3166-1 alpha-2 country code where the individual is from.

        Returns:
        dict: SDN API response.
        """
        params_dict = {
            'sources': self.sdn_api_list,
            'type': 'individual',
            'name': str(name).encode('utf-8'),
            # We are using the city as the address parameter value as indicated in the documentation:
            # https://internationaltradeadministration.github.io/developerportal/consolidated-screening-list.html
            'city': str(city).encode('utf-8'),
            'countries': country
        }
        params = urlencode(params_dict)
        sdn_check_url = '{api_url}?{params}'.format(
            api_url=self.sdn_api_url,
            params=params
        )
        auth_header = {'subscription-key': '{}'.format(self.sdn_api_key)}

        try:
            logger.info(
                'Sactions SDNCheck: starting the request to the US Treasury SDN API for %s.',
                lms_user_id
            )
            response = requests.get(
                sdn_check_url,
                headers=auth_header,
                timeout=settings.SDN_CHECK_REQUEST_TIMEOUT
            )
        except requests.exceptions.Timeout:
            logger.warning(
                'Sanctions SDNCheck: Connection to the US Treasury SDN API timed out for [%s].',
                name
            )
            raise

        if response.status_code != 200:
            logger.warning(
                'Sanctions SDNCheck: Unable to connect to the US Treasury SDN API for [%s].'
                'Status code [%d] with message: [%s]',
                name, response.status_code, response.content
            )
            raise requests.exceptions.HTTPError('Unable to connect to the SDN API')

        return response.json()
