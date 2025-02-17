"""
Django management command to download SDN CSV for use as fallback if the trade.gov SDN API is down.
"""
import logging
import tempfile

import opsgenie_sdk
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from requests.exceptions import Timeout

from sanctions.apps.sanctions.utils import populate_sdn_fallback_data_and_metadata

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Command to download the SDN CSV to be saved as a fallback. Runs every 15 minutes.
    """
    help = 'Download the SDN CSV from trade.gov, for use as fallback for when their SDN API is down.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            metavar='N',
            action='store',
            type=float,
            default=3,  # typical size is > 4 MB; 3 MB would be unexpectedly low
            help='File size MB threshold, under which we will not import it. Use default if argument not specified'
        )

    def _hit_opsgenie_heartbeat(self):
        """
        Hit OpsGenie heartbeat to indicate that the fallback job has run successfully recently.
        """
        og_sdk_config = opsgenie_sdk.configuration.Configuration()
        og_sdk_config.api_key['Authorization'] = settings.OPSGENIE_API_KEY
        og_api_client = opsgenie_sdk.api_client.ApiClient(configuration=og_sdk_config)
        og_heartbeat_api = opsgenie_sdk.HeartbeatApi(api_client=og_api_client)

        heartbeat_name = settings.OPSGENIE_HEARTBEAT_NAME

        logger.info(f'Calling opsgenie heartbeat for {heartbeat_name}')
        response = og_heartbeat_api.ping(heartbeat_name)
        logger.info(f'request id: {response.request_id}')
        logger.info(f'took: {response.took}')
        logger.info(f'result: {response.result}')

    def handle(self, *args, **options):
        # download the CSV locally, to check size and pass along to import
        threshold = options['threshold']
        url = settings.CONSOLIDATED_SCREENING_LIST_URL
        timeout = settings.SDN_BACKUP_REQUEST_TIMEOUT

        with requests.Session() as s:
            try:
                download = s.get(url, timeout=timeout)
                status_code = download.status_code
            except Timeout:
                logger.warning(
                    "Sanctions SDNFallback: DOWNLOAD FAILURE: Timeout occurred trying to download SDN CSV. "
                    "Timeout threshold (in seconds): %s", timeout)
                raise
            except Exception as e:
                logger.exception("Sanctions SDNFallback: DOWNLOAD FAILURE: Exception occurred: [%s]", e)
                raise

            if download.status_code != 200:
                logger.warning("Sanctions SDNFallback: DOWNLOAD FAILURE: Status code was: [%s]", status_code)
                raise Exception("CSV download url got an unsuccessful response code: ", status_code)

            with tempfile.TemporaryFile() as temp_csv:
                temp_csv.write(download.content)
                file_size_in_bytes = temp_csv.tell()  # get current position in the file (number of bytes)
                file_size_in_MB = file_size_in_bytes / 10**6

                if file_size_in_MB > threshold:
                    sdn_file_string = download.content.decode('utf-8')
                    with transaction.atomic():
                        metadata_entry = populate_sdn_fallback_data_and_metadata(sdn_file_string)
                        if metadata_entry:
                            logger.info(
                                'Sanctions SDNFallback: IMPORT SUCCESS: Imported SDN CSV. Metadata id %s',
                                metadata_entry.id)

                        logger.info('Sanctions SDNFallback: DOWNLOAD SUCCESS: Successfully downloaded the SDN CSV.')
                        self.stdout.write(
                            self.style.SUCCESS(
                                "Sanctions SDNFallback: Imported SDN CSV into the SDNFallbackMetadata"
                                " and SDNFallbackData models."
                            )
                        )
                        self._hit_opsgenie_heartbeat()
                else:
                    logger.warning(
                        "Sanctions SDNFallback: DOWNLOAD FAILURE: file too small! "
                        "(%f MB vs threshold of %s MB)", file_size_in_MB, threshold)
                    raise Exception("CSV file download did not meet threshold given")
