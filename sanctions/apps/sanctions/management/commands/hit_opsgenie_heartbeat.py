"""
Dummy management command to prove we can hit an opsgenie heart beat from a cronjob
"""
import logging

import opsgenie_sdk
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy management command to prove we can hit an opsgenie heart beat from a cronjob
    """
    help = (
        'Dummy management command to prove we can hit an opsgenie heart beat from a cronjob'
    )

    def handle(self, *args, **options):
        og_sdk_config = opsgenie_sdk.configuration.Configuration()
        og_sdk_config.api_key['Authorization'] = settings.OPSGENIE_API_KEY
        og_api_client = opsgenie_sdk.api_client.ApiClient(configuration=og_sdk_config)
        og_heartbeat_api = opsgenie_sdk.HeartbeatApi(api_client=og_api_client)

        heartbeat_name = 'sanctions-sdn-fallback-job'

        logger.info(f'Calling opsgenie heartbeat for {heartbeat_name}')
        response = og_heartbeat_api.ping(heartbeat_name)
        logger.info(f'request id: {response.request_id}')
        logger.info(f'took: {response.took}')
        logger.info(f'result: {response.result}')
