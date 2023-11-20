"""
Django management command to delete all metadata records.
"""
import logging

from django.core.management.base import BaseCommand

from sanctions.apps.sanctions.models import SanctionsCheckFailure

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Command to delete all SanctionsCheckFailure records.
    """
    help = 'Delete all SanctionsCheckFailure records.'

    def handle(self, *args, **options):
        logger.info('Beginning deletion of SanctionsCheckFailure records.')
        all_records = SanctionsCheckFailure.objects.all().iterator()

        for record in all_records:
            logger.info('Deleting record %s', record.id)
            record.delete()
            logger.info('Deleted record %s', record.id)

        logger.info('Completed deletion of SanctionsCheckFailure records.')
