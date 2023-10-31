"""
API v1 Views
"""
import logging

from django.conf import settings
from django.http import JsonResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from requests.exceptions import HTTPError, Timeout
from rest_framework import permissions, views

from sanctions.apps.api_client.sdn_client import SDNClient

logger = logging.getLogger(__name__)


class SDNCheckView(views.APIView):
    """
    View for external services to run SDN/ISN checks against.
    """
    http_method_names = ['post']
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JwtAuthentication,)

    def post(self, request):
        """
        Receive billing information data and perform SDN/ISN checks against trade.gov API.

        Returns a hit count.
        """
        payload = request.data

        # Make sure we have the values needed to carry out the request
        missing_args = []
        for expected_arg in ['lms_user_id', 'full_name', 'city', 'country']:
            if not payload.get(expected_arg):
                missing_args.append(expected_arg)
        if missing_args:
            json_data = {
                'missing_args': ', '.join(missing_args)
            }
            return JsonResponse(json_data, status=400)

        lms_user_id = request.user.lms_user_id
        full_name = payload.get('full_name')
        city = payload.get('city')
        country = payload.get('country')
        sdn_api_list = payload.get('sdn_api_list', 'ISN,SDN')  # Set SDN lists to a sane default

        sdn_check = SDNClient(
            sdn_api_url=settings.SDN_CHECK_API_URL,
            sdn_api_key=settings.SDN_CHECK_API_KEY,
            sdn_api_list=sdn_api_list
        )

        try:
            logger.info(
                'SDNCheckView: calling the SDN Client for SDN check for user %s.',
                lms_user_id
            )
            response = sdn_check.search(lms_user_id, full_name, city, country)
        except (HTTPError, Timeout) as e:
            logger.info(
                'SDNCheckView: SDN API call received an error: %s.'
                ' Calling SanctionsFallback function for user %s.',
                str(e),
                lms_user_id
            )

            # Temp: return 400 until the SDN Fallback check logic is implemented.
            json_data = {
                'error': e,
            }
            return JsonResponse(json_data, status=400)

            # TODO: add SDN fallback check to determine hit count.

        hit_count = response['total']
        if hit_count > 0:
            logger.info(
                'SDNCheckView request received for lms user [%s]. It received %d hit(s).',
                lms_user_id,
                hit_count,
            )
        else:
            logger.info(
                'SDNCheckView request received for lms user [%s]. It did not receive a hit.',
                lms_user_id,
            )

        json_data = {
            'hit_count': hit_count,
            'sdn_response': response,
        }

        return JsonResponse(json_data, status=200)
