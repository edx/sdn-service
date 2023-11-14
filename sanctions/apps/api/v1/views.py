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
from sanctions.apps.sanctions.models import SanctionsCheckFailure
from sanctions.apps.sanctions.utils import checkSDNFallback

logger = logging.getLogger(__name__)


class SDNCheckView(views.APIView):
    """
    View for external services to run SDN/ISN checks against.
    """
    http_method_names = ['post']
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
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

        lms_user_id = payload.get('lms_user_id')
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
            sdn_check_response = sdn_check.search(lms_user_id, full_name, city, country)
        except (HTTPError, Timeout) as e:
            logger.info(
                'SDNCheckView: SDN API call received an error: %s.'
                ' Calling sanctions checkSDNFallback function for user %s.',
                str(e),
                lms_user_id
            )

            sdn_fallback_hit_count = checkSDNFallback(
                full_name,
                city,
                country
            )
            sdn_check_response = {'total': sdn_fallback_hit_count}

        hit_count = sdn_check_response['total']
        if hit_count > 0:
            logger.info(
                'SDNCheckView request received for lms user [%s]. It received %d hit(s).',
                lms_user_id,
                hit_count,
            )
            # write record to our DB that we've had a positive hit, including
            # any metadata provided in the payload
            metadata = payload.get('metadata', {})
            username = payload.get('username')
            system_identifier = payload.get('system_identifier')
            sanctions_type = 'ISN,SDN'
            # This try/except is here to make us fault tolerant. Callers of this
            # API should not be held up if we are having DB troubles. Log the error
            # and continue through the code to reply to them.
            try:
                SanctionsCheckFailure.objects.create(
                    full_name=full_name,
                    username=username,
                    lms_user_id=lms_user_id,
                    city=city,
                    country=country,
                    sanctions_type=sanctions_type,
                    system_identifier=system_identifier,
                    metadata=metadata,
                    sanctions_response=sdn_check_response,
                )
            except Exception as err:  # pylint: disable=broad-exception-caught
                error_message = (
                    'Encountered error creating SanctionsCheckFailure. %s '
                    'Data dump follows to capture information on the hit: '
                    'lms_user_id: %s '
                    'username: %s '
                    'full_name: %s '
                    'city: %s '
                    'country: %s '
                    'sanctions_type: %s '
                    'system_identifier: %s '
                    'metadata: %s '
                    'sanctions_response: %s '
                )
                logger.exception(
                    error_message,
                    err,
                    lms_user_id,
                    username,
                    full_name,
                    city,
                    country,
                    sanctions_type,
                    system_identifier,
                    metadata,
                    sdn_check_response,
                )
        else:
            logger.info(
                'SDNCheckView request received for lms user [%s]. It did not receive a hit.',
                lms_user_id,
            )

        json_data = {
            'hit_count': hit_count,
            'sdn_response': sdn_check_response,
        }

        return JsonResponse(json_data, status=200)
